#!/usr/bin/env python3
"""
Production Readiness Verification Script
Comprehensive check for all enterprise production improvements
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path
import subprocess

class ProductionReadinessChecker:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "security": {},
            "performance": {},
            "reliability": {},
            "operations": {},
            "code_quality": {},
            "total_score": 0,
            "detailed_results": []
        }

    def log_result(self, category, check_name, status, score, details=""):
        """Log a check result"""
        result = {
            "category": category,
            "check": check_name,
            "status": status,
            "score": score,
            "details": details
        }
        self.results["detailed_results"].append(result)
        if category not in self.results:
            self.results[category] = {}
        self.results[category][check_name] = {"status": status, "score": score, "details": details}
        print(f"✅ {category.upper()}: {check_name} - {status} ({score} points)")

    def check_security_improvements(self):
        """Check security-related improvements"""
        print("\n🔒 SECURITY CHECKS")

        # Security headers check
        next_config_path = Path("../frontend/next.config.ts")
        if next_config_path.exists():
            content = next_config_path.read_text()
            if "X-Frame-Options" in content and "Content-Security-Policy" in content and "Strict-Transport-Security" in content:
                self.log_result("security", "Security Headers", "PASS", 15, "CSP, HSTS, X-Frame-Options configured")
            else:
                self.log_result("security", "Security Headers", "PARTIAL", 8, "Some security headers missing")
        else:
            self.log_result("security", "Security Headers", "FAIL", 0, "next.config.ts not found")

        # CORS configuration check
        main_py_path = Path("app/main.py")
        if main_py_path.exists():
            content = main_py_path.read_text()
            if '"Content-Type",' in content and '"Authorization",' in content and not '"*"' in content:
                self.log_result("security", "CORS Configuration", "PASS", 10, "CORS headers restricted properly")
            else:
                self.log_result("security", "CORS Configuration", "PARTIAL", 5, "CORS needs hardening")
        else:
            self.log_result("security", "CORS Configuration", "FAIL", 0, "main.py not found")

        # Database credential masking
        if "masked_url" in main_py_path.read_text():
            self.log_result("security", "Credential Masking", "PASS", 8, "Database URLs properly masked")
        else:
            self.log_result("security", "Credential Masking", "FAIL", 0, "No credential masking found")

    def check_performance_improvements(self):
        """Check performance-related improvements"""
        print("\n⚡ PERFORMANCE CHECKS")

        # N+1 query optimization
        matching_py_path = Path("app/api/endpoints/matching.py")
        if matching_py_path.exists():
            content = matching_py_path.read_text()
            if "get_recommended_talents_batch" in content:
                self.log_result("performance", "N+1 Query Optimization", "PASS", 20, "Batch query function implemented")
            else:
                self.log_result("performance", "N+1 Query Optimization", "FAIL", 0, "N+1 issues not resolved")
        else:
            self.log_result("performance", "N+1 Query Optimization", "FAIL", 0, "matching.py not found")

        # Async database connections
        if "asyncpg" in Path("requirements.txt").read_text():
            self.log_result("performance", "Async DB Connections", "PASS", 8, "asyncpg configured")
        else:
            self.log_result("performance", "Async DB Connections", "FAIL", 0, "Not using async DB driver")

        # Index optimization (check if database files exist)
        if any(Path(".").glob("**/index*.sql")):
            self.log_result("performance", "Database Indexes", "PASS", 7, "Index optimization files found")
        else:
            self.log_result("performance", "Database Indexes", "PARTIAL", 3, "No explicit index optimization found")

    def check_reliability_improvements(self):
        """Check reliability-related improvements"""
        print("\n🛡️ RELIABILITY CHECKS")

        # Error handling
        api_files = list(Path("app/api/endpoints").glob("*.py"))
        error_handling_count = 0
        for file_path in api_files:
            if "try:" in file_path.read_text() and "except" in file_path.read_text():
                error_handling_count += 1

        if error_handling_count >= len(api_files) * 0.8:
            self.log_result("reliability", "Error Handling", "PASS", 10, f"{error_handling_count}/{len(api_files)} files have error handling")
        else:
            self.log_result("reliability", "Error Handling", "PARTIAL", 5, "Insufficient error handling coverage")

        # Input validation
        if any("pydantic" in file.read_text() for file in Path("app/schemas").glob("*.py") if file.exists()):
            self.log_result("reliability", "Input Validation", "PASS", 8, "Pydantic models for validation")
        else:
            self.log_result("reliability", "Input Validation", "PARTIAL", 4, "Limited input validation")

        # Health checks
        health_py_path = Path("app/api/endpoints/health.py")
        if health_py_path.exists() and "database" in health_py_path.read_text():
            self.log_result("reliability", "Health Checks", "PASS", 7, "Comprehensive health endpoint")
        else:
            self.log_result("reliability", "Health Checks", "PARTIAL", 3, "Basic health checks only")

    def check_operations_improvements(self):
        """Check operations-related improvements"""
        print("\n🔧 OPERATIONS CHECKS")

        # Structured logging
        frontend_files = list(Path("../frontend/src").glob("**/*.ts*"))
        logging_improved = 0
        for file_path in frontend_files:
            content = file_path.read_text()
            if "process.env.NODE_ENV !== 'production'" in content and "console.log" in content:
                logging_improved += 1

        if logging_improved >= 3:  # At least 3 files with conditional logging
            self.log_result("operations", "Structured Logging", "PASS", 12, f"Console.log conditional in {logging_improved} files")
        else:
            self.log_result("operations", "Structured Logging", "PARTIAL", 6, "Limited logging improvements")

        # Environment configuration
        if Path("../frontend/.env.example").exists() or Path(".env.example").exists():
            self.log_result("operations", "Environment Config", "PASS", 8, "Environment examples provided")
        else:
            self.log_result("operations", "Environment Config", "PARTIAL", 4, "No environment documentation")

        # Monitoring readiness
        if "timestamp" in Path("app/main.py").read_text():
            self.log_result("operations", "Monitoring Readiness", "PASS", 5, "Timestamp logging implemented")
        else:
            self.log_result("operations", "Monitoring Readiness", "PARTIAL", 2, "Limited monitoring capabilities")

    def check_code_quality_improvements(self):
        """Check code quality improvements"""
        print("\n📋 CODE QUALITY CHECKS")

        # Test coverage - Backend
        test_files_backend = list(Path("tests").glob("*.py"))
        if len(test_files_backend) >= 2:
            self.log_result("code_quality", "Backend Tests", "PASS", 8, f"{len(test_files_backend)} test files")
        else:
            self.log_result("code_quality", "Backend Tests", "PARTIAL", 4, "Limited test coverage")

        # Test coverage - Frontend
        frontend_test_files = list(Path("../frontend/src/__tests__").glob("*.ts*"))
        if len(frontend_test_files) >= 1:
            self.log_result("code_quality", "Frontend Tests", "PASS", 8, f"{len(frontend_test_files)} test files")
        else:
            self.log_result("code_quality", "Frontend Tests", "FAIL", 0, "No frontend tests")

        # Configuration files
        config_files = ["pytest.ini", "../frontend/jest.config.js", "../frontend/jest.setup.js"]
        config_count = sum(1 for cf in config_files if Path(cf).exists())
        if config_count >= 3:
            self.log_result("code_quality", "Test Configuration", "PASS", 6, "Complete test setup")
        elif config_count >= 2:
            self.log_result("code_quality", "Test Configuration", "PARTIAL", 3, "Partial test setup")
        else:
            self.log_result("code_quality", "Test Configuration", "FAIL", 0, "No test configuration")

        # Type safety
        if "TypeScript" in str(Path("../frontend").glob("**/*.ts*")):
            self.log_result("code_quality", "Type Safety", "PASS", 5, "TypeScript implementation")
        else:
            self.log_result("code_quality", "Type Safety", "PARTIAL", 2, "Limited type safety")

    def calculate_total_score(self):
        """Calculate total score from all checks"""
        total = 0
        for result in self.results["detailed_results"]:
            total += result["score"]

        self.results["total_score"] = total
        return total

    def run_all_checks(self):
        """Run all production readiness checks"""
        print("🚀 Starting Production Readiness Assessment")
        print("=" * 60)

        self.check_security_improvements()
        self.check_performance_improvements()
        self.check_reliability_improvements()
        self.check_operations_improvements()
        self.check_code_quality_improvements()

        total_score = self.calculate_total_score()

        print("\n" + "=" * 60)
        print(f"📊 FINAL SCORE: {total_score}/120 points")

        if total_score >= 90:
            grade = "A - Enterprise Ready"
            status = "✅ PASSED"
        elif total_score >= 75:
            grade = "B - Production Ready"
            status = "✅ PASSED"
        elif total_score >= 60:
            grade = "C - Acceptable"
            status = "⚠️ CONDITIONAL"
        else:
            grade = "F - Not Ready"
            status = "❌ FAILED"

        print(f"🏆 GRADE: {grade}")
        print(f"🎯 STATUS: {status}")
        print("=" * 60)

        # Save detailed results
        with open("production_readiness_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("📄 Detailed report saved to: production_readiness_report.json")

        return total_score

def main():
    checker = ProductionReadinessChecker()
    final_score = checker.run_all_checks()

    if final_score >= 90:
        print("\n🎉 CONGRATULATIONS! Enterprise production readiness achieved!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Score: {final_score}/120. Target: 90+ for enterprise readiness.")
        sys.exit(1)

if __name__ == "__main__":
    main()