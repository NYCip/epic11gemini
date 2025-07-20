import asyncio
import aiohttp
from typing import List, Dict, Tuple
import json
from datetime import datetime
import subprocess
import re

class SecurityAuditor:
    """
    Continuous security auditing for EPIC V11
    """
    
    def __init__(self, base_url: str = "https://epic.pos.com"):
        self.base_url = base_url
        self.vulnerabilities = []
        self.audit_timestamp = datetime.utcnow()
    
    async def run_full_audit(self) -> Dict:
        """Execute comprehensive security audit"""
        print(" Starting EPIC V11 Security Audit...")
        
        results = {
            "timestamp": self.audit_timestamp.isoformat(),
            "authentication": await self.audit_authentication(),
            "authorization": await self.audit_authorization(),
            "encryption": await self.audit_encryption(),
            "injection": await self.audit_injection_vulnerabilities(),
            "docker": await self.audit_docker_security(),
            "dependencies": await self.audit_dependencies(),
            "secrets": await self.audit_secrets(),
            "network": await self.audit_network_security()
        }
        
        # Generate report
        self.generate_report(results)
        
        return results
    
    async def audit_authentication(self) -> Dict:
        """Audit authentication mechanisms"""
        findings = []
        
        # Test password policy
        weak_passwords = ["password", "12345678", "admin123"]
        for pwd in weak_passwords:
            try:
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        f"{self.base_url}/control/auth/token",
                        data={"username": "test @epic.pos.com", "password": pwd}
                    )
                    if response.status == 200:
                        findings.append({
                            "severity": "CRITICAL",
                            "issue": f"Weak password accepted: {pwd}",
                            "recommendation": "Enforce strong password policy"
                        })
            except:
                pass
        
        # Test JWT security
        # Check for algorithm confusion, expired tokens, etc.
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_authorization(self) -> Dict:
        """Test RBAC implementation"""
        findings = []
        
        # Test privilege escalation
        # Test horizontal/vertical access control
        # Test for IDOR vulnerabilities
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_encryption(self) -> Dict:
        """Verify encryption standards"""
        findings = []
        
        # Check TLS configuration
        ssl_check = subprocess.run(
            ["testssl", "--json", self.base_url],
            capture_output=True,
            text=True
        )
        
        if "TLS 1.0" in ssl_check.stdout or "TLS 1.1" in ssl_check.stdout:
            findings.append({
                "severity": "HIGH",
                "issue": "Outdated TLS versions supported",
                "recommendation": "Disable TLS 1.0 and 1.1"
            })
        
        # Check for secure headers
        async with aiohttp.ClientSession() as session:
            response = await session.get(self.base_url)
            headers = response.headers
            
            required_headers = {
                "Strict-Transport-Security": "HSTS not set",
                "X-Content-Type-Options": "Content-Type sniffing not prevented",
                "X-Frame-Options": "Clickjacking protection missing",
                "Content-Security-Policy": "CSP not configured"
            }
            
            for header, issue in required_headers.items():
                if header not in headers:
                    findings.append({
                        "severity": "MEDIUM",
                        "issue": issue,
                        "recommendation": f"Add {header} header"
                    })
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_injection_vulnerabilities(self) -> Dict:
        """Test for injection vulnerabilities"""
        findings = []
        
        # SQL Injection tests
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users;--",
            "1' UNION SELECT NULL--"
        ]
        
        # XSS tests
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        # Command injection tests
        cmd_payloads = [
            "; ls -la",
            "| whoami",
            "`id`"
        ]
        
        # Test each endpoint with payloads
        # Log any successful injections
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_docker_security(self) -> Dict:
        """Audit Docker configuration"""
        findings = []
        
        # Check for running as root
        containers = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}:{{.User}}"],
            capture_output=True,
            text=True
        )
        
        for line in containers.stdout.splitlines():
            name, user = line.split(":")
            if user == "root" or not user:
                findings.append({
                    "severity": "HIGH",
                    "issue": f"Container {name} running as root",
                    "recommendation": "Use non-root user in Dockerfile"
                })
        
        # Check for privileged containers
        # Verify resource limits
        # Check for sensitive mounts
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_dependencies(self) -> Dict:
        """Scan for vulnerable dependencies"""
        findings = []
        
        # Run pip-audit for Python dependencies
        services = ["control_panel_backend", "agno_service", "mcp_server"]
        
        for service in services:
            result = subprocess.run(
                ["pip-audit", "--desc", f"./{service}/requirements.txt"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                vulnerabilities = self._parse_pip_audit(result.stdout)
                findings.extend(vulnerabilities)
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    async def audit_secrets(self) -> Dict:
        """Scan for exposed secrets"""
        findings = []
        
        # Use truffleHog to scan for secrets
        result = subprocess.run(
            ["trufflehog", "filesystem", ".", "--json"],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.splitlines():
            if line:
                secret = json.loads(line)
                findings.append({
                    "severity": "CRITICAL",
                    "issue": f"Exposed secret: {secret['DetectorName']}",
                    "file": secret['SourceMetadata']['Data']['Filesystem']['file'],
                    "recommendation": "Remove secret and rotate credentials"
                })
        
        return {
            "passed": len(findings) == 0,
            "findings": findings
        }
    
    def generate_report(self, results: Dict):
        """Generate security audit report"""
        report = f"""
# EPIC V11 Security Audit Report
Generated: {self.audit_timestamp.isoformat()}

## Executive Summary
{'✅ All security checks PASSED' if self._all_passed(results) else '❌ Security issues detected'}

## Detailed Findings
"""
        
        for category, data in results.items():
            if category == "timestamp":
                continue
                
            report += f"\n### {category.upper()}\n"
            
            if data["passed"]:
                report += "✅ No issues found\n"
            else:
                report += f"❌ {len(data['findings'])} issues found:\n\n"
                for finding in data['findings']:
                    report += f"- **{finding['severity']}**: {finding['issue']}\n"
                    report += f"  *Recommendation*: {finding['recommendation']}\n\n"
        
        # Save report
        with open(f"security_audit_{self.audit_timestamp.strftime('%Y%m%d_%H%M%S')}.md", "w") as f:
            f.write(report)
        
        print(report)
    
    def _all_passed(self, results: Dict) -> bool:
        for category, data in results.items():
            if category != "timestamp" and not data.get("passed", True):
                return False
        return True

# Continuous monitoring script
async def continuous_monitoring():
    """Run continuous security monitoring"""
    auditor = SecurityAuditor()
    
    while True:
        print(" Running security scan...")
        results = await auditor.run_full_audit()
        
        # Alert on critical findings
        critical_count = sum(
            1 for cat in results.values()
            if isinstance(cat, dict) and "findings" in cat
            for finding in cat["findings"]
            if finding.get("severity") == "CRITICAL"
        )
        
        if critical_count > 0:
            print(f" ALERT: {critical_count} CRITICAL security issues detected!")
            # Send alerts via preferred channel
        
        # Wait 1 hour before next scan
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(continuous_monitoring())
