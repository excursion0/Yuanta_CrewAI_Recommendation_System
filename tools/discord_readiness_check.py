#!/usr/bin/env python3
"""
Discord Bot Readiness Check Utility

This script checks if the Discord bot is ready to use by validating
environment variables, file structure, and module dependencies.
"""

import os
import sys
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import constants and exceptions with fallback
try:
    from src.constants import ERROR_MESSAGES, SUCCESS_MESSAGES
    from src.exceptions import ConfigurationError, ImportError as CustomImportError
except ImportError:
    # Fallback if src module not available
    ERROR_MESSAGES = {
        "import_failed": "Failed to import required module: {}",
        "api_key_missing": "API key not found in environment variables",
        "timeout_error": "Operation timed out after {} seconds",
        "validation_failed": "Data validation failed: {}",
        "connection_failed": "Failed to connect to {}: {}",
        "processing_error": "Error processing request: {}"
    }
    SUCCESS_MESSAGES = {
        "bot_ready": "Discord bot is ready to use!",
        "api_configured": "API configured successfully",
        "test_passed": "Test passed successfully",
        "import_successful": "Import successful"
    }
    ConfigurationError = Exception
    CustomImportError = ImportError


class DiscordReadinessChecker:
    """Utility class for checking Discord bot readiness."""
    
    def __init__(self):
        """Initialize the readiness checker."""
        self.logger = logging.getLogger(__name__)
        self.results = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """
        Check if required environment variables are set.
        
        Returns:
            Dict[str, Any]: Environment check results
        """
        self.logger.info("Checking environment variables...")
        
        # Load environment variables
        load_dotenv()
        
        required_vars = {
            "DISCORD_BOT_TOKEN": "Discord Bot Token",
            "ANTHROPIC_API_KEY": "Anthropic API Key"
        }
        
        results = {
            "status": "pass",
            "missing": [],
            "found": []
        }
        
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if value:
                results["found"].append(f"{description}: ✅ Set")
            else:
                results["missing"].append(f"{description}: ❌ Not set")
                results["status"] = "fail"
        
        self.results["environment"] = results
        return results
    
    def check_required_files(self) -> Dict[str, Any]:
        """
        Check if required files exist.
        
        Returns:
            Dict[str, Any]: File check results
        """
        self.logger.info("Checking required files...")
        
        required_files = [
            "src/chatbot/discord_bot.py",
            "discord_bot_main.py",
            "requirements.txt"
        ]
        
        results = {
            "status": "pass",
            "missing": [],
            "found": []
        }
        
        for file_path in required_files:
            if os.path.exists(file_path):
                results["found"].append(f"{file_path}: ✅ Found")
            else:
                results["missing"].append(f"{file_path}: ❌ Missing")
                results["status"] = "fail"
        
        self.results["files"] = results
        return results
    
    def check_module_dependencies(self) -> Dict[str, Any]:
        """
        Check if required modules can be imported.
        
        Returns:
            Dict[str, Any]: Module check results
        """
        self.logger.info("Checking module dependencies...")
        
        results = {
            "status": "pass",
            "failed": [],
            "successful": []
        }
        
        # Check discord.py
        try:
            import discord
            results["successful"].append("discord.py: ✅ Available")
        except ImportError as e:
            results["failed"].append(f"discord.py: ❌ Not installed - {e}")
            results["status"] = "fail"
        
        # Check FinancialDiscordBot
        try:
            from src.chatbot.discord_bot import FinancialDiscordBot
            results["successful"].append("FinancialDiscordBot: ✅ Available")
        except Exception as e:
            results["failed"].append(f"FinancialDiscordBot: ❌ Import error - {e}")
            results["status"] = "fail"
        
        self.results["modules"] = results
        return results
    
    def run_full_check(self) -> Dict[str, Any]:
        """
        Run all readiness checks.
        
        Returns:
            Dict[str, Any]: Complete check results
        """
        self.logger.info("🔍 DISCORD BOT READINESS CHECK")
        self.logger.info("=" * 50)
        
        # Run all checks
        env_results = self.check_environment_variables()
        file_results = self.check_required_files()
        module_results = self.check_module_dependencies()
        
        # Determine overall status
        overall_status = "pass"
        if any(result["status"] == "fail" for result in [env_results, file_results, module_results]):
            overall_status = "fail"
        
        # Compile results
        full_results = {
            "overall_status": overall_status,
            "environment": env_results,
            "files": file_results,
            "modules": module_results,
            "summary": self._generate_summary()
        }
        
        self.results = full_results
        return full_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the check results.
        
        Returns:
            Dict[str, Any]: Summary information
        """
        env_status = self.results.get("environment", {}).get("status", "unknown")
        file_status = self.results.get("files", {}).get("status", "unknown")
        module_status = self.results.get("modules", {}).get("status", "unknown")
        
        env_ready = env_status == "pass"
        files_ready = file_status == "pass"
        modules_ready = module_status == "pass"
        
        summary = {
            "environment_configured": env_ready,
            "required_files_present": files_ready,
            "required_modules_importable": modules_ready,
            "ready_to_use": all([env_ready, files_ready, modules_ready])
        }
        
        return summary
    
    def print_results(self) -> None:
        """Print the check results in a formatted way."""
        if not self.results:
            self.logger.error("No results available. Run check first.")
            return
        
        # Print environment results
        env_results = self.results.get("environment", {})
        self.logger.info("Environment Variables:")
        for found in env_results.get("found", []):
            self.logger.info(f"  {found}")
        for missing in env_results.get("missing", []):
            self.logger.error(f"  {missing}")
        
        # Print file results
        file_results = self.results.get("files", {})
        self.logger.info("\nRequired Files:")
        for found in file_results.get("found", []):
            self.logger.info(f"  {found}")
        for missing in file_results.get("missing", []):
            self.logger.error(f"  {missing}")
        
        # Print module results
        module_results = self.results.get("modules", {})
        self.logger.info("\nModule Dependencies:")
        for successful in module_results.get("successful", []):
            self.logger.info(f"  {successful}")
        for failed in module_results.get("failed", []):
            self.logger.error(f"  {failed}")
        
        # Print summary
        summary = self.results.get("summary", {})
        self.logger.info("\n🎯 READINESS ASSESSMENT:")
        
        if summary.get("environment_configured"):
            self.logger.info("✅ Environment variables are configured")
        else:
            self.logger.error("❌ Missing required environment variables")
        
        if summary.get("required_files_present"):
            self.logger.info("✅ Required files are present")
        else:
            self.logger.error("❌ Some required files are missing")
        
        if summary.get("required_modules_importable"):
            self.logger.info("✅ Required modules can be imported")
        else:
            self.logger.error("❌ Module import issues detected")
        
        # Final assessment
        if summary.get("ready_to_use"):
            self.logger.info(f"\n🎉 {SUCCESS_MESSAGES['bot_ready']}")
            self.logger.info("   You can run: python discord_bot_main.py")
        else:
            self.logger.error("\n⚠️ DISCORD BOT NEEDS CONFIGURATION")
            self.logger.error("   Please check the issues above before running the bot")


def main():
    """Main function to run the Discord bot readiness check."""
    checker = DiscordReadinessChecker()
    
    try:
        results = checker.run_full_check()
        checker.print_results()
        
        # Return appropriate exit code
        if results.get("overall_status") == "pass":
            return 0
        else:
            return 1
            
    except Exception as e:
        logging.error(f"Error during readiness check: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
