# FlowSpec Support - Advanced Traffic Filtering

## Overview

FlowSpec (Flow Specification) is a BGP extension (RFC 5575) that allows fine-grained traffic filtering policies to be distributed via BGP. Unlike traditional BGP blackholing (RTBH) which drops all traffic to a specific IP, FlowSpec enables selective filtering based on:

- Source and destination IP addresses
- Protocols (TCP, UDP, ICMP, etc.)
- Port numbers (source and destination)
- TCP flags
- Packet length
- DSCP values
- Fragment types

## Benefits

- **Granular Control**: Filter specific attack traffic while allowing legitimate traffic
- **Distributed Mitigation**: Rules propagate via BGP to all routers in the network
- **Fast Deployment**: Near-instant mitigation once BGP converges
- **Protocol-Aware**: Target specific attack vectors (e.g., SYN floods, DNS amplification)
- **Reduced Collateral Damage**: Unlike RTBH, legitimate traffic can continue flowing

## Prerequisites

1. **BGP Session**: Established BGP peering with upstream provider or internal routers
2. **FlowSpec Support**: BGP daemon must support FlowSpec (ExaBGP, FRR recommended)
3. **Router Compatibility**: Routers must support FlowSpec filtering
4. **Configuration**: BGP FlowSpec address-family must be enabled

## Supported BGP Daemons

### ExaBGP (Recommended)

ExaBGP has excellent FlowSpec support and is easiest to integrate.

**Configuration** (`/etc/exabgp/exabgp.conf`):

```ini
process announce-flows {
    run /usr/local/bin/exabgp-flowspec.sh;
    encoder json;
}

neighbor 198.51.100.1 {
    router-id 203.0.113.1;
    local-address 203.0.113.1;
    local-as 64512;
    peer-as 64496;
    
    family {
        ipv4 flow;
        ipv6 flow;
    }
    
    api {
        processes [announce-flows];
    }
}
```

**Features Supported**:
- ✅ Source/destination prefixes
- ✅ Protocol filtering
- ✅ Port specifications
- ✅ TCP flags
- ✅ Packet length
- ✅ DSCP values
- ✅ Fragment types
- ✅ Rate limiting actions

### FRR (Free Range Routing)

FRR supports FlowSpec starting from version 7.5.

**Configuration** (`/etc/frr/frr.conf`):

```
router bgp 64512
 bgp router-id 203.0.113.1
 neighbor 198.51.100.1 remote-as 64496
 
 address-family ipv4 flowspec
  neighbor 198.51.100.1 activate
 exit-address-family
```

**Features Supported**:
- ✅ Source/destination prefixes
- ✅ Protocol filtering
- ✅ Port specifications
- ⚠️ Limited TCP flags support
- ⚠️ Rate limiting via extended communities

### BIRD

BIRD FlowSpec support is limited and not yet implemented in this platform.

## Configuration

### Backend Configuration

Update `backend/.env`:

```bash
# Enable BGP and FlowSpec
BGP_ENABLED=true
BGP_DAEMON=exabgp  # or frr

# ExaBGP settings
EXABGP_CMD_PIPE=/var/run/exabgp.cmd

# FRR settings
FRR_VTYSH_CMD=/usr/bin/vtysh
```

Update `backend/config.py` (already configured):

```python
# BGP Configuration
BGP_ENABLED = os.getenv("BGP_ENABLED", "false").lower() == "true"
BGP_DAEMON = os.getenv("BGP_DAEMON", "exabgp")
```

## Usage

### Via API

#### Basic FlowSpec Rule

Block all TCP traffic to a specific destination:

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 123,
    "action_type": "flowspec",
    "details": {
      "destination": "203.0.113.50/32",
      "protocol": "tcp",
      "action": "drop"
    }
  }'
```

#### Port-Specific Filtering

Block SYN flood attacks on port 80:

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 124,
    "action_type": "flowspec",
    "details": {
      "destination": "203.0.113.50/32",
      "protocol": "tcp",
      "dest_port": 80,
      "tcp_flags": "syn",
      "action": "drop"
    }
  }'
```

#### DNS Amplification Mitigation

Block UDP traffic on port 53 from specific source:

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 125,
    "action_type": "flowspec",
    "details": {
      "source": "198.51.100.0/24",
      "destination": "203.0.113.0/24",
      "protocol": "udp",
      "dest_port": 53,
      "action": "drop"
    }
  }'
```

#### Rate Limiting

Rate limit instead of dropping:

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 126,
    "action_type": "flowspec",
    "details": {
      "destination": "203.0.113.50/32",
      "protocol": "tcp",
      "dest_port": 443,
      "action": "rate-limit 10000"
    }
  }'
```

#### Packet Length Filtering

Block small packets (common in some attacks):

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 127,
    "action_type": "flowspec",
    "details": {
      "destination": "203.0.113.50/32",
      "protocol": "udp",
      "packet_length": "<64",
      "action": "drop"
    }
  }'
```

#### Execute Mitigation

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/1/execute \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Withdraw FlowSpec Rule

```bash
curl -X POST http://localhost:8000/api/v1/mitigations/1/stop \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Via Python Script

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def block_syn_flood(target_ip: str, port: int, alert_id: int):
    """Block SYN flood attacks on specific port"""
    
    # Create FlowSpec mitigation
    response = requests.post(
        f"{API_URL}/mitigations/",
        headers=headers,
        json={
            "alert_id": alert_id,
            "action_type": "flowspec",
            "details": {
                "destination": f"{target_ip}/32",
                "protocol": "tcp",
                "dest_port": port,
                "tcp_flags": "syn",
                "action": "drop"
            }
        }
    )
    
    if response.status_code == 200:
        mitigation_id = response.json()["id"]
        
        # Execute mitigation
        exec_response = requests.post(
            f"{API_URL}/mitigations/{mitigation_id}/execute",
            headers=headers
        )
        
        print(f"FlowSpec mitigation active: {exec_response.json()}")
        return mitigation_id
    else:
        print(f"Error: {response.text}")
        return None

# Example usage
mitigation_id = block_syn_flood("203.0.113.50", 80, alert_id=123)
```

## FlowSpec Parameters

### Required Parameters

- `destination`: Destination IP prefix in CIDR notation (e.g., "203.0.113.50/32")
- `action`: Action to take ("drop" or "rate-limit <bps>")

### Optional Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `source` | string | Source IP prefix | "198.51.100.0/24" |
| `protocol` | string | IP protocol | "tcp", "udp", "icmp", "6", "17" |
| `source_port` | int | Source port number | 80, 443 |
| `dest_port` | int | Destination port number | 80, 443 |
| `packet_length` | string | Packet length range | "<64", ">=64&<=128" |
| `dscp` | int | DSCP value | 46 (EF), 0 (BE) |
| `fragment` | string | Fragment type | "not-a-fragment", "is-fragment" |
| `tcp_flags` | string | TCP flags | "syn", "ack", "fin", "rst" |

### Actions

- **drop**: Drop all matching packets
- **rate-limit <bps>**: Rate limit to specified bits per second
  - `rate-limit 0`: Same as drop
  - `rate-limit 10000`: Limit to 10 Kbps

## Common Use Cases

### 1. Mitigate SYN Flood

```json
{
  "destination": "203.0.113.50/32",
  "protocol": "tcp",
  "dest_port": 80,
  "tcp_flags": "syn",
  "action": "drop"
}
```

### 2. Stop UDP Amplification

```json
{
  "source": "0.0.0.0/0",
  "destination": "203.0.113.0/24",
  "protocol": "udp",
  "dest_port": 53,
  "packet_length": ">512",
  "action": "drop"
}
```

### 3. Block ICMP Floods

```json
{
  "destination": "203.0.113.50/32",
  "protocol": "icmp",
  "action": "drop"
}
```

### 4. Rate Limit Suspicious Traffic

```json
{
  "source": "198.51.100.0/24",
  "destination": "203.0.113.50/32",
  "protocol": "tcp",
  "action": "rate-limit 1000000"
}
```

### 5. Block Fragmented Packets

```json
{
  "destination": "203.0.113.0/24",
  "fragment": "is-fragment",
  "action": "drop"
}
```

## Verification

### Check ExaBGP Status

```bash
# View ExaBGP logs
tail -f /var/log/exabgp.log

# Check active flows
cat /var/run/exabgp.cmd
```

### Check FRR Status

```bash
# View BGP FlowSpec routes
sudo vtysh -c "show bgp ipv4 flowspec"

# View detailed flow
sudo vtysh -c "show bgp ipv4 flowspec 203.0.113.50/32"
```

### Verify at Router

Most routers have commands to view active FlowSpec rules:

**Cisco:**
```
show bgp ipv4 flowspec
show flowspec ipv4
```

**Juniper:**
```
show route table inetflow.0
show firewall filter __flowspec_default_inet__
```

## Troubleshooting

### FlowSpec Not Working

**Check BGP session:**
```bash
# ExaBGP
tail -f /var/log/exabgp.log | grep flowspec

# FRR
sudo vtysh -c "show bgp ipv4 flowspec summary"
```

**Check FlowSpec capability:**
```bash
# Verify FlowSpec is negotiated
sudo vtysh -c "show bgp neighbor 198.51.100.1"
# Look for: "ipv4 flow" in capabilities
```

**Check command pipe (ExaBGP):**
```bash
ls -la /var/run/exabgp.cmd
# Should exist and be writable
```

### Rules Not Applied

**Verify router support:**
- Confirm router supports FlowSpec filtering
- Check if FlowSpec address-family is enabled
- Verify action (drop, rate-limit) is supported

**Check permissions:**
```bash
# ExaBGP pipe must be writable
sudo chown ddos:exabgp /var/run/exabgp.cmd
sudo chmod 660 /var/run/exabgp.cmd
```

### API Errors

**"FlowSpec is disabled"**
- Set `BGP_ENABLED=true` in `.env`
- Restart backend

**"Invalid prefix format"**
- Use CIDR notation (e.g., "192.0.2.1/32")
- Validate IP address format

**"ExaBGP not running"**
- Check ExaBGP service: `sudo systemctl status exabgp`
- Verify pipe exists: `ls -la /var/run/exabgp.cmd`

## Best Practices

### 1. Start Specific, Expand if Needed

```python
# Good: Target specific attack
{"destination": "203.0.113.50/32", "protocol": "tcp", "dest_port": 80, "tcp_flags": "syn"}

# Careful: Very broad rule
{"destination": "203.0.113.0/24", "protocol": "tcp"}
```

### 2. Use Rate Limiting for Uncertain Traffic

When you're not sure if traffic is malicious, rate limit first:

```python
# Rate limit suspicious traffic
{"destination": "203.0.113.50/32", "action": "rate-limit 1000000"}

# Monitor, then drop if confirmed attack
{"destination": "203.0.113.50/32", "action": "drop"}
```

### 3. Monitor Active Rules

```bash
# List active FlowSpec mitigations
curl -X GET "http://localhost:8000/api/v1/mitigations/?action_type=flowspec&status=active" \
  -H "Authorization: Bearer TOKEN"
```

### 4. Withdraw Rules After Attack

FlowSpec rules should be temporary. Withdraw them when attack subsides:

```python
# Automatically withdraw after 30 minutes
import time

mitigation_id = create_flowspec_rule(...)
time.sleep(1800)  # 30 minutes
withdraw_flowspec_rule(mitigation_id)
```

### 5. Coordinate with Upstream

- Confirm upstream supports FlowSpec
- Verify which actions are supported (drop, rate-limit, redirect)
- Test during maintenance window
- Document FlowSpec contact for issues

## Security Considerations

### Validation

All FlowSpec parameters are validated to prevent:
- Invalid IP addresses/prefixes
- Command injection
- Malformed BGP announcements

### Access Control

Only authorized users can create FlowSpec rules:

```python
if current_user.role not in ["admin", "operator"]:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Audit Logging

All FlowSpec actions are logged:

```python
audit_log = {
    "action": "flowspec_announce",
    "user": current_user.username,
    "destination": destination,
    "timestamp": datetime.utcnow()
}
```

## Comparison: FlowSpec vs RTBH

| Feature | FlowSpec | RTBH (Blackhole) |
|---------|----------|------------------|
| **Granularity** | High (protocol, port, flags) | Low (entire IP) |
| **Collateral Damage** | Minimal | Significant |
| **Complexity** | Moderate | Low |
| **Router Support** | Limited | Universal |
| **Setup Difficulty** | Moderate | Easy |
| **Use Case** | Targeted mitigation | Quick drops |
| **Speed** | Fast (BGP convergence) | Fast (BGP convergence) |

**When to use FlowSpec:**
- Need to allow legitimate traffic
- Attack is protocol/port specific
- Have FlowSpec-capable routers
- Want fine-grained control

**When to use RTBH:**
- Need immediate blanket protection
- All traffic to IP is unwanted
- Simple setup preferred
- Universal router compatibility needed

## References

- **RFC 5575**: Dissemination of Flow Specification Rules
- **RFC 7674**: Clarification of BGP Flowspec
- **ExaBGP FlowSpec**: https://github.com/Exa-Networks/exabgp/wiki/Flowspec
- **FRR FlowSpec**: https://docs.frrouting.org/en/latest/flowspec.html

## Support

For FlowSpec-related issues:
- Check logs: `tail -f /var/log/exabgp.log`
- Platform logs: `docker-compose logs -f backend`
- GitHub Issues: https://github.com/i4edubd/ddos-protection/issues
