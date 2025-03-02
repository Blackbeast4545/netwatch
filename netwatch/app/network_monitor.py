import threading
import time
from datetime import datetime
import json
import socket
import subprocess
import psutil
from scapy.all import sniff, IP, TCP, UDP, ICMP
from . import socketio
from .geo_ip import GeoIPLookup

class NetworkMonitor:
    def __init__(self):
        self.packet_counts = {
            'TCP': 0,
            'UDP': 0,
            'ICMP': 0,
            'Other': 0
        }
        self.max_history = 15
        self.traffic_history = []
        self.packet_history = []
        self.running = False
        self.last_bytes_sent = psutil.net_io_counters().bytes_sent
        self.last_bytes_recv = psutil.net_io_counters().bytes_recv
        self.last_check_time = time.time()
        self.connections = []
        self.system_stats = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_used': 0,
            'memory_total': 0
        }
        self.geo_ip = GeoIPLookup()
        # Start packet capture thread
        self.capture_thread = None

    def packet_callback(self, packet):
        try:
            if IP in packet:
                if TCP in packet:
                    self.packet_counts['TCP'] += 1
                elif UDP in packet:
                    self.packet_counts['UDP'] += 1
                elif ICMP in packet:
                    self.packet_counts['ICMP'] += 1
                else:
                    self.packet_counts['Other'] += 1
        except Exception as e:
            print(f"Error in packet callback: {str(e)}")

    def start_packet_capture(self):
        try:
            # Start packet capture in non-blocking mode
            sniff(prn=self.packet_callback, store=0, filter="ip", count=0)
        except Exception as e:
            print(f"Error starting packet capture: {str(e)}")

    def get_active_connections(self):
        try:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                try:
                    if conn.status == 'ESTABLISHED':
                        try:
                            # Get process information if PID exists
                            if conn.pid:
                                process = psutil.Process(conn.pid)
                                process_name = process.name()
                            else:
                                process_name = "Unknown"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"

                        # Get remote IP without port
                        remote_ip = conn.raddr.ip if conn.raddr else None
                        
                        # Skip if no remote address
                        if not remote_ip:
                            continue

                        # Format addresses with ports
                        local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                        remote_addr = f"{remote_ip}:{conn.raddr.port}"
                        
                        # Get location data for non-local addresses
                        location = None
                        if not remote_ip.startswith(('127.', '192.168.', '10.', '172.')):
                            location = self.geo_ip.get_location(remote_ip)
                        
                        connection_info = {
                            'local_addr': local_addr,
                            'remote_addr': remote_addr,
                            'status': conn.status,
                            'process': process_name,  # Just use process name without PID
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'location': location
                        }
                        connections.append(connection_info)
                except Exception as e:
                    print(f"Error processing connection: {str(e)}")
                    continue
                
            # Sort connections by timestamp (newest first)
            connections.sort(key=lambda x: x['timestamp'], reverse=True)
            return connections[:15]  # Return only the latest 15 connections
        
        except Exception as e:
            print(f"Error getting active connections: {str(e)}")
            return []

    def get_system_stats(self):
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total

            # Get disk usage for all partitions
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'total': self.format_bytes(usage.total),
                        'used': self.format_bytes(usage.used),
                        'free': self.format_bytes(usage.free),
                        'percent': usage.percent
                    })
                except:
                    continue

            self.system_stats = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used': self.format_bytes(memory_used),
                'memory_total': self.format_bytes(memory_total),
                'disk_info': disk_info
            }
            return self.system_stats
        except Exception as e:
            print(f"Error getting system stats: {str(e)}")
            return self.system_stats

    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024

    def get_network_traffic(self):
        try:
            current_time = time.time()
            net_io = psutil.net_io_counters()
            
            # Calculate bytes sent/received since last check
            bytes_sent = net_io.bytes_sent - self.last_bytes_sent
            bytes_recv = net_io.bytes_recv - self.last_bytes_recv
            
            # Calculate time difference
            time_diff = current_time - self.last_check_time
            
            # Calculate rates (bytes per second)
            bytes_sent_rate = int(bytes_sent / time_diff)
            bytes_recv_rate = int(bytes_recv / time_diff)
            
            # Update last values
            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
            self.last_check_time = current_time
            
            return {
                'bytes_sent': bytes_sent_rate,
                'bytes_recv': bytes_recv_rate
            }
        except Exception as e:
            print(f"Error getting network traffic: {str(e)}")
            return {'bytes_sent': 0, 'bytes_recv': 0}

    def start(self):
        self.running = True
        # Start packet capture thread
        self.capture_thread = threading.Thread(target=self.start_packet_capture)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()

    def monitor_system(self):
        print("Starting system monitoring...")
        while self.running:
            try:
                current_time = datetime.now().strftime('%H:%M:%S')
                
                # Get fresh data
                system_stats = self.get_system_stats()
                active_connections = self.get_active_connections()  # Get fresh connections
                traffic_data = self.get_network_traffic()
                
                # Update packet history
                current_packets = {
                    'timestamp': current_time,
                    'TCP': self.packet_counts['TCP'],
                    'UDP': self.packet_counts['UDP'],
                    'ICMP': self.packet_counts['ICMP'],
                    'Other': self.packet_counts['Other']
                }
                
                self.packet_history.append(current_packets)
                self.packet_history = self.packet_history[-self.max_history:]

                # Update traffic history
                traffic_data['timestamp'] = current_time
                self.traffic_history.append(traffic_data)
                self.traffic_history = self.traffic_history[-self.max_history:]

                # Create update data
                data = {
                    'timestamp': current_time,
                    'connections': active_connections,  # Use fresh connections
                    'packet_counts': self.packet_counts.copy(),
                    'packet_history': self.packet_history,
                    'traffic_history': self.traffic_history,
                    'current_traffic': {
                        'bytes_sent_rate': traffic_data['bytes_sent'],
                        'bytes_recv_rate': traffic_data['bytes_recv']
                    },
                    'system_stats': system_stats
                }

                # Emit update
                socketio.emit('network_update', data)
                
                time.sleep(1)  # Update every second

            except Exception as e:
                print(f"Error in monitor_system: {str(e)}")
                time.sleep(1)

    def stop(self):
        self.running = False 