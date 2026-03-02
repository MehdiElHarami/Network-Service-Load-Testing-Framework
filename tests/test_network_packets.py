"""
Network packet-level testing using Scapy
This module provides advanced network testing capabilities including:
- Packet capture and analysis
- Custom packet crafting
- Network latency testing
- Packet loss simulation
"""
import time
from typing import Optional, Dict, Any
try:
    from scapy.all import IP, TCP, ICMP, sr1, send, sniff
    from scapy.layers.http import HTTP, HTTPRequest
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: Scapy not available. Install with: pip install scapy")

class NetworkPacketTester:
    """Advanced network packet testing"""
    
    def __init__(self, target_host: str = "127.0.0.1", target_port: int = 8000):
        self.target_host = target_host
        self.target_port = target_port
        
        if not SCAPY_AVAILABLE:
            raise ImportError("Scapy is required for network packet testing")
    
    def ping_test(self, count: int = 4) -> Dict[str, Any]:
        """
        ICMP ping test to measure network latency
        
        Args:
            count: Number of ping packets to send
            
        Returns:
            Dict with latency statistics
        """
        if not SCAPY_AVAILABLE:
            return {"error": "Scapy not available"}
        
        latencies = []
        
        for i in range(count):
            packet = IP(dst=self.target_host)/ICMP()
            
            start = time.time()
            reply = sr1(packet, timeout=2, verbose=0)
            
            if reply:
                latency = (time.time() - start) * 1000
                latencies.append(latency)
            
        if latencies:
            return {
                "target": self.target_host,
                "packets_sent": count,
                "packets_received": len(latencies),
                "packet_loss": ((count - len(latencies)) / count) * 100,
                "min_latency_ms": round(min(latencies), 2),
                "max_latency_ms": round(max(latencies), 2),
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2)
            }
        else:
            return {
                "target": self.target_host,
                "packets_sent": count,
                "packets_received": 0,
                "packet_loss": 100.0,
                "error": "No responses received"
            }
    
    def tcp_syn_scan(self) -> Dict[str, Any]:
        """
        TCP SYN scan to check if port is open
        
        Returns:
            Dict with port status
        """
        if not SCAPY_AVAILABLE:
            return {"error": "Scapy not available"}

        packet = IP(dst=self.target_host)/TCP(dport=self.target_port, flags="S")

        start = time.time()
        reply = sr1(packet, timeout=2, verbose=0)
        latency = (time.time() - start) * 1000
        
        if reply and reply.haslayer(TCP):
            if reply[TCP].flags == "SA":
                rst = IP(dst=self.target_host)/TCP(dport=self.target_port, flags="R")
                send(rst, verbose=0)
                
                return {
                    "target": f"{self.target_host}:{self.target_port}",
                    "status": "open",
                    "response_time_ms": round(latency, 2)
                }
            elif reply[TCP].flags == "RA":
                return {
                    "target": f"{self.target_host}:{self.target_port}",
                    "status": "closed",
                    "response_time_ms": round(latency, 2)
                }
        
        return {
            "target": f"{self.target_host}:{self.target_port}",
            "status": "filtered/no-response",
            "response_time_ms": round(latency, 2)
        }
    
    def measure_tcp_handshake(self) -> Dict[str, Any]:
        """
        Measure TCP 3-way handshake time
        
        Returns:
            Dict with handshake timing
        """
        if not SCAPY_AVAILABLE:
            return {"error": "Scapy not available"}

        start = time.time()
        syn = IP(dst=self.target_host)/TCP(dport=self.target_port, flags="S", seq=1000)
        syn_ack = sr1(syn, timeout=2, verbose=0)
        
        if not syn_ack or not syn_ack.haslayer(TCP):
            return {"error": "No SYN-ACK received"}
        
        ack = IP(dst=self.target_host)/TCP(
            dport=self.target_port, 
            flags="A", 
            seq=syn_ack[TCP].ack, 
            ack=syn_ack[TCP].seq + 1
        )
        send(ack, verbose=0)
        
        handshake_time = (time.time() - start) * 1000

        fin = IP(dst=self.target_host)/TCP(
            dport=self.target_port, 
            flags="FA", 
            seq=syn_ack[TCP].ack, 
            ack=syn_ack[TCP].seq + 1
        )
        send(fin, verbose=0)
        
        return {
            "target": f"{self.target_host}:{self.target_port}",
            "handshake_time_ms": round(handshake_time, 2),
            "status": "success"
        }
    
    def packet_capture(self, duration: int = 10, filter_str: str = "tcp") -> Dict[str, Any]:
        """
        Capture network packets for analysis
        
        Args:
            duration: Capture duration in seconds
            filter_str: BPF filter string
            
        Returns:
            Dict with capture statistics
        """
        if not SCAPY_AVAILABLE:
            return {"error": "Scapy not available"}
        
        print(f"Capturing packets for {duration} seconds...")
        packets = sniff(timeout=duration, filter=filter_str)

        protocols = {}
        packet_sizes = []
        
        for packet in packets:
            if packet.haslayer(TCP):
                protocols["TCP"] = protocols.get("TCP", 0) + 1
            if packet.haslayer(IP):
                packet_sizes.append(len(packet))
        
        return {
            "total_packets": len(packets),
            "capture_duration_seconds": duration,
            "protocols": protocols,
            "avg_packet_size_bytes": round(sum(packet_sizes) / len(packet_sizes), 2) if packet_sizes else 0,
            "total_bytes": sum(packet_sizes)
        }


def run_network_diagnostics(host: str = "127.0.0.1", port: int = 8000) -> Dict[str, Any]:
    """
    Run comprehensive network diagnostics
    
    Args:
        host: Target host
        port: Target port
        
    Returns:
        Dict with all test results
    """
    if not SCAPY_AVAILABLE:
        return {
            "error": "Scapy not available. Install with: pip install scapy",
            "note": "Scapy requires admin/root privileges for some operations"
        }
    
    tester = NetworkPacketTester(host, port)
    
    results = {
        "target": f"{host}:{port}",
        "timestamp": time.time(),
        "tests": {}
    }
    
    try:
        results["tests"]["icmp_ping"] = tester.ping_test(count=4)
    except Exception as e:
        results["tests"]["icmp_ping"] = {"error": str(e)}
    
    try:
        results["tests"]["tcp_syn_scan"] = tester.tcp_syn_scan()
    except Exception as e:
        results["tests"]["tcp_syn_scan"] = {"error": str(e)}
    
    try:
        results["tests"]["tcp_handshake"] = tester.measure_tcp_handshake()
    except Exception as e:
        results["tests"]["tcp_handshake"] = {"error": str(e)}
    
    return results


if __name__ == "__main__":
    print("Running network diagnostics...")
    print("Note: Some tests require admin/root privileges")
    
    results = run_network_diagnostics()
    
    import json
    print(json.dumps(results, indent=2))
