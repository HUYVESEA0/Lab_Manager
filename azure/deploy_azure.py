#!/usr/bin/env python3
"""
Simple Azure App Service Deployment Script
Deploy Lab Manager to Azure App Service
"""

import os
import sys
import subprocess
import json

def print_banner():
    print("""
╔═══════════════════════════════════════════════╗
║        Lab Manager - Azure Deployment         ║
║           Simple & Effective Setup             ║
╚═══════════════════════════════════════════════╝
""")

def run_command(cmd, description):
    """Run command with error handling"""
    print(f"\n🔄 {description}...")
    print(f"📟 Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Details: {e.stderr.strip()}")
        return None

def check_prerequisites():
    """Check required tools"""
    print("\n🔍 Checking prerequisites...")
    
    # Check Azure CLI
    result = run_command("az --version", "Checking Azure CLI")
    if not result:
        print("❌ Azure CLI not found. Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check login
    result = run_command("az account show", "Checking Azure login")
    if not result:
        print("🔐 Please login first: az login")
        return False
    
    print("✅ Prerequisites check passed!")
    return True

def get_deployment_info():
    """Get deployment configuration from user"""
    print("\n📝 Deployment Configuration:")
    
    app_name = input("🏷️  App name (e.g., lab-manager-demo): ").strip()
    if not app_name:
        app_name = "lab-manager-demo"
    
    location = input("🌍 Location (default: Southeast Asia): ").strip()
    if not location:
        location = "southeastasia"
    
    resource_group = f"{app_name}-rg"
    plan_name = f"{app_name}-plan"
    
    return {
        'app_name': app_name,
        'resource_group': resource_group,
        'location': location,
        'plan_name': plan_name
    }

def create_azure_resources(config):
    """Create Azure resources"""
    print(f"\n🏗️  Creating Azure resources...")
    
    # Create resource group
    cmd = f"az group create --name {config['resource_group']} --location {config['location']}"
    if not run_command(cmd, "Creating Resource Group"):
        return False
    
    # Create App Service Plan (B1 Basic for better performance)
    cmd = f"az appservice plan create --name {config['plan_name']} --resource-group {config['resource_group']} --sku B1 --is-linux"
    if not run_command(cmd, "Creating App Service Plan"):
        return False
    
    # Create Web App
    cmd = f"az webapp create --name {config['app_name']} --resource-group {config['resource_group']} --plan {config['plan_name']} --runtime 'PYTHON|3.11'"
    if not run_command(cmd, "Creating Web App"):
        return False
    
    return True

def configure_webapp(config):
    """Configure Web App settings"""
    print(f"\n⚙️  Configuring Web App...")
    
    # Set startup command
    cmd = f"az webapp config set --name {config['app_name']} --resource-group {config['resource_group']} --startup-file 'run_azure.py'"
    run_command(cmd, "Setting startup file")
    
    # Configure app settings
    settings = [
        "WEBSITES_PORT=8000",
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
        "ENABLE_ORYX_BUILD=true",
        "FLASK_ENV=production",
        "FLASK_DEBUG=0"
    ]
    
    for setting in settings:
        cmd = f"az webapp config appsettings set --name {config['app_name']} --resource-group {config['resource_group']} --settings {setting}"
        run_command(cmd, f"Setting {setting.split('=')[0]}")

def deploy_code(config):
    """Deploy source code"""
    print(f"\n🚀 Deploying source code...")
    
    # Ensure git repository
    if not os.path.exists('.git'):
        run_command("git init", "Initializing Git")
        run_command("git add .", "Adding files")
        run_command('git commit -m "Initial commit for Azure"', "Creating commit")
    
    # Configure deployment source
    cmd = f"az webapp deployment source config-local-git --name {config['app_name']} --resource-group {config['resource_group']}"
    result = run_command(cmd, "Configuring Git deployment")
    
    if result and result.stdout:
        # Extract Git URL and deploy
        import re
        git_url_match = re.search(r'https://.*?\.git', result.stdout)
        if git_url_match:
            git_url = git_url_match.group()
            run_command(f"git remote add azure {git_url}", "Adding Azure remote")
            
            print("\n🚀 Pushing to Azure (this may take a few minutes)...")
            push_result = run_command("git push azure main", "Deploying to Azure")
            
            if push_result:
                print("✅ Deployment successful!")
                return True
            else:
                print("⚠️  Push failed. Try: git push azure main --force")
    
    return False

def show_results(config):
    """Show deployment results"""
    print(f"""
╔═══════════════════════════════════════════════╗
║            🎉 DEPLOYMENT COMPLETED!           ║
╚═══════════════════════════════════════════════╝

🌐 Your Lab Manager is live at:
   https://{config['app_name']}.azurewebsites.net

📋 Azure Resources:
   • Resource Group: {config['resource_group']}
   • App Service: {config['app_name']}
   • Service Plan: {config['plan_name']} (B1 Basic)
   • Location: {config['location']}

🔧 Useful Commands:
   az webapp browse --name {config['app_name']} --resource-group {config['resource_group']}
   az webapp log tail --name {config['app_name']} --resource-group {config['resource_group']}

🎯 Next Steps:
   1. Test your application
   2. Configure custom domain (optional)
   3. Set up monitoring and alerts
   4. Configure database (upgrade from SQLite if needed)
""")

def main():
    """Main deployment function"""
    print_banner()
    
    if not check_prerequisites():
        sys.exit(1)
    
    config = get_deployment_info()
    
    print(f"\n📋 Deployment Summary:")
    print(f"   App Name: {config['app_name']}")
    print(f"   Resource Group: {config['resource_group']}")
    print(f"   Location: {config['location']}")
    print(f"   Plan: B1 Basic (~$13/month)")
    
    confirm = input("\n🚀 Deploy now? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Deployment cancelled.")
        sys.exit(0)
    
    try:
        if not create_azure_resources(config):
            sys.exit(1)
        
        configure_webapp(config)
        
        if deploy_code(config):
            show_results(config)
        else:
            print("❌ Deployment failed. Check errors above.")
            
    except KeyboardInterrupt:
        print("\n❌ Deployment interrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main()
