"""
System resource monitoring module for Ollama GUI
Provides real-time tracking of CPU, RAM, and GPU usage with visualization
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil
try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False

class SystemMonitor:
    """Monitors and displays system resource usage"""
    
    def __init__(self, parent, update_interval=1000):
        """
        Initialize the system monitor
        
        Args:
            parent: Parent application reference
            update_interval: Update interval in milliseconds
        """
        self.parent = parent
        self.update_interval = update_interval
        self.running = True
        
        # Create main frame
        self.frame = tk.LabelFrame(
            parent.system_monitor_frame, 
            text="System Resources", 
            bg=parent.bg_color,
            fg=parent.text_color,
            font=("TkDefaultFont", 7, "bold"),
        )
        
        # CPU monitor
        self.cpu_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.cpu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cpu_label = ttk.Label(
            self.cpu_frame, 
            text="CPU Usage:", 
            background=parent.bg_color,
            foreground=parent.text_color,
            font=("TkDefaultFont", 7)
        )
        self.cpu_label.pack(side=tk.LEFT)
        
        self.cpu_progress = ttk.Progressbar(
            self.cpu_frame, 
            orient=tk.HORIZONTAL, 
            length=150, 
            mode='determinate'
        )
        self.cpu_progress.pack(side=tk.LEFT, padx=5)
        
        self.cpu_percentage = ttk.Label(
            self.cpu_frame, 
            text="0%", 
            background=parent.bg_color,
            foreground=parent.found_color,
            font=("TkDefaultFont", 7, "bold")
        )
        self.cpu_percentage.pack(side=tk.LEFT, padx=5)
        
        # RAM monitor
        self.ram_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.ram_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ram_label = ttk.Label(
            self.ram_frame, 
            text="RAM Usage:", 
            background=parent.bg_color,
            foreground=parent.text_color,
            font=("TkDefaultFont", 7)
        )
        self.ram_label.pack(side=tk.LEFT)
        
        self.ram_progress = ttk.Progressbar(
            self.ram_frame, 
            orient=tk.HORIZONTAL, 
            length=150, 
            mode='determinate'
        )
        self.ram_progress.pack(side=tk.LEFT, padx=5)
        
        self.ram_percentage = ttk.Label(
            self.ram_frame, 
            text="0%", 
            background=parent.bg_color,
            foreground=parent.found_color,
            font=("TkDefaultFont", 7, "bold")
        )
        self.ram_percentage.pack(side=tk.LEFT, padx=5)
        
        # GPU monitor (if available)
        self.gpu_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.gpu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if HAS_GPU:
            self.gpu_label = ttk.Label(
                self.gpu_frame, 
                text="GPU Usage:", 
                background=parent.bg_color,
                foreground=parent.text_color,
                font=("TkDefaultFont", 7)
            )
            self.gpu_label.pack(side=tk.LEFT)
            
            self.gpu_progress = ttk.Progressbar(
                self.gpu_frame, 
                orient=tk.HORIZONTAL, 
                length=150, 
                mode='determinate'
            )
            self.gpu_progress.pack(side=tk.LEFT, padx=5)
            
            self.gpu_percentage = ttk.Label(
                self.gpu_frame, 
                text="0%", 
                background=parent.bg_color,
                foreground=parent.found_color,
                font=("TkDefaultFont", 7, "bold")
            )
            self.gpu_percentage.pack(side=tk.LEFT, padx=5)
            
            # GPU Memory
            self.gpu_mem_frame = tk.Frame(self.frame, bg=parent.bg_color)
            self.gpu_mem_frame.pack(fill=tk.X, padx=10, pady=5)
            
            self.gpu_mem_label = ttk.Label(
                self.gpu_mem_frame, 
                text="GPU Memory:", 
                background=parent.bg_color,
                foreground=parent.text_color,
                font=("TkDefaultFont", 7)
            )
            self.gpu_mem_label.pack(side=tk.LEFT)
            
            self.gpu_mem_progress = ttk.Progressbar(
                self.gpu_mem_frame, 
                orient=tk.HORIZONTAL, 
                length=150, 
                mode='determinate'
            )
            self.gpu_mem_progress.pack(side=tk.LEFT, padx=5)
            
            self.gpu_mem_percentage = ttk.Label(
                self.gpu_mem_frame, 
                text="0%", 
                background=parent.bg_color,
                foreground=parent.found_color,
                font=("TkDefaultFont", 7, "bold")
            )
            self.gpu_mem_percentage.pack(side=tk.LEFT, padx=5)
        else:
            self.gpu_status = ttk.Label(
                self.gpu_frame, 
                text="GPU monitoring unavailable (install GPUtil package)", 
                background=parent.bg_color,
                foreground=parent.not_found_color,
                font=("TkDefaultFont", 7)
            )
            self.gpu_status.pack(side=tk.LEFT)
        
        # Start monitoring thread
        self.update_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.update_thread.start()
    
    def _monitor_resources(self):
        """Background thread for resource monitoring"""
        while self.running:
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.5)
                
                # Get RAM usage
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                
                # Update UI in main thread
                self.parent.master.after(0, lambda: self._update_ui(cpu_percent, ram_percent))
                
                # Get GPU usage if available
                if HAS_GPU:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]  # Get primary GPU
                            gpu_percent = gpu.load * 100
                            gpu_mem_percent = gpu.memoryUtil * 100
                            self.parent.master.after(0, lambda: self._update_gpu_ui(gpu_percent, gpu_mem_percent))
                    except Exception as e:
                        pass
                
                # Sleep until next update
                time.sleep(self.update_interval / 1000)
            except Exception as e:
                # Avoid crashing the thread on errors
                pass
    
    def _update_ui(self, cpu_percent, ram_percent):
        """Update the UI with current system resource usage"""
        # Update CPU
        self.cpu_progress['value'] = cpu_percent
        self.cpu_percentage.config(text=f"{cpu_percent:.1f}%")
        
        # Set color based on usage
        if cpu_percent > 80:
            self.cpu_percentage.config(foreground=self.parent.not_found_color)
        elif cpu_percent > 50:
            self.cpu_percentage.config(foreground=self.parent.checking_color)
        else:
            self.cpu_percentage.config(foreground=self.parent.found_color)
        
        # Update RAM
        self.ram_progress['value'] = ram_percent
        self.ram_percentage.config(text=f"{ram_percent:.1f}%")
        
        # Set color based on usage
        if ram_percent > 80:
            self.ram_percentage.config(foreground=self.parent.not_found_color)
        elif ram_percent > 50:
            self.ram_percentage.config(foreground=self.parent.checking_color)
        else:
            self.ram_percentage.config(foreground=self.parent.found_color)
    
    def _update_gpu_ui(self, gpu_percent, gpu_mem_percent):
        """Update the UI with GPU usage information"""
        if not HAS_GPU:
            return
            
        # Update GPU usage
        self.gpu_progress['value'] = gpu_percent
        self.gpu_percentage.config(text=f"{gpu_percent:.1f}%")
        
        # Set color based on usage
        if gpu_percent > 80:
            self.gpu_percentage.config(foreground=self.parent.not_found_color)
        elif gpu_percent > 50:
            self.gpu_percentage.config(foreground=self.parent.checking_color)
        else:
            self.gpu_percentage.config(foreground=self.parent.found_color)
        
        # Update GPU memory
        self.gpu_mem_progress['value'] = gpu_mem_percent
        self.gpu_mem_percentage.config(text=f"{gpu_mem_percent:.1f}%")
        
        # Set color based on usage
        if gpu_mem_percent > 80:
            self.gpu_mem_percentage.config(foreground=self.parent.not_found_color)
        elif gpu_mem_percent > 50:
            self.gpu_mem_percentage.config(foreground=self.parent.checking_color)
        else:
            self.gpu_mem_percentage.config(foreground=self.parent.found_color)
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)

class ModelMetricsMonitor:
    """Monitors and displays Ollama model metrics"""
    
    def __init__(self, parent):
        """
        Initialize the model metrics monitor
        
        Args:
            parent: Parent application reference
        """
        self.parent = parent
        
        # Create main frame
        self.frame = tk.LabelFrame(
            parent.model_metrics_frame, 
            text="Model Performance Metrics", 
            bg=parent.bg_color,
            fg=parent.text_color,
            font=("TkDefaultFont", 7, "bold")
        )
        
        # Token generation metrics
        self.token_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.token_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.token_rate_label = ttk.Label(
            self.token_frame, 
            text="Generation Speed:", 
            background=parent.bg_color,
            foreground=parent.text_color,
            font=("TkDefaultFont", 7)
        )
        self.token_rate_label.pack(side=tk.LEFT)
        
        self.token_rate_value = ttk.Label(
            self.token_frame, 
            text="0 tokens/s", 
            background=parent.bg_color,
            foreground=parent.found_color,
            font=("TkDefaultFont", 7, "bold")
        )
        self.token_rate_value.pack(side=tk.LEFT, padx=5)
        
        # Latency metrics
        self.latency_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.latency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.latency_label = ttk.Label(
            self.latency_frame, 
            text="Response Latency:", 
            background=parent.bg_color,
            foreground=parent.text_color,
            font=("TkDefaultFont", 7)
        )
        self.latency_label.pack(side=tk.LEFT)
        
        self.latency_value = ttk.Label(
            self.latency_frame, 
            text="0 ms", 
            background=parent.bg_color,
            foreground=parent.found_color,
            font=("TkDefaultFont", 7, "bold")
        )
        self.latency_value.pack(side=tk.LEFT, padx=5)
        
        # Memory usage
        self.memory_frame = tk.Frame(self.frame, bg=parent.bg_color)
        self.memory_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.memory_label = ttk.Label(
            self.memory_frame, 
            text="Model Memory:", 
            background=parent.bg_color,
            foreground=parent.text_color,
            font=("TkDefaultFont", 7)
        )
        self.memory_label.pack(side=tk.LEFT)
        
        self.memory_value = ttk.Label(
            self.memory_frame, 
            text="0 MB", 
            background=parent.bg_color,
            foreground=parent.found_color,
            font=("TkDefaultFont", 7, "bold")
        )
        self.memory_value.pack(side=tk.LEFT, padx=5)
    
    def update_metrics(self, token_rate=0, latency=0, memory_usage=0):
        """
        Update the displayed metrics
        
        Args:
            token_rate (float): Token generation rate in tokens/s
            latency (float): Response latency in milliseconds
            memory_usage (float): Memory usage in MB
        """
        # Update token rate
        self.token_rate_value.config(text=f"{token_rate:.1f} tokens/s")
        
        # Update latency
        self.latency_value.config(text=f"{latency:.1f} ms")
        
        # Update memory usage
        self.memory_value.config(text=f"{memory_usage:.1f} MB")
        
        # Set colors based on performance
        # Token rate
        if token_rate > 20:
            self.token_rate_value.config(foreground=self.parent.found_color)
        elif token_rate > 5:
            self.token_rate_value.config(foreground=self.parent.checking_color)
        else:
            self.token_rate_value.config(foreground=self.parent.not_found_color)
            
        # Latency
        if latency < 100:
            self.latency_value.config(foreground=self.parent.found_color)
        elif latency < 500:
            self.latency_value.config(foreground=self.parent.checking_color)
        else:
            self.latency_value.config(foreground=self.parent.not_found_color)