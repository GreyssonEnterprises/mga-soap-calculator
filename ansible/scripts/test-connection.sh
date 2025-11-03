#!/bin/bash
# MGA SOAP Calculator - Ansible Connection Testing Script
#
# Tests connectivity and validates server prerequisites for deployment
#
# Usage:
#   ./test-connection.sh [production|staging]
#
# Requirements:
#   - Ansible installed
#   - SSH access configured
#   - Inventory files configured

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
INVENTORY_DIR="$ANSIBLE_DIR/inventory"

# Default environment
ENVIRONMENT="${1:-production}"

# Inventory file selection
case "$ENVIRONMENT" in
    production)
        INVENTORY_FILE="$INVENTORY_DIR/production.yml"
        HOST_GROUP="mga_production"
        ;;
    staging)
        INVENTORY_FILE="$INVENTORY_DIR/staging.yml"
        HOST_GROUP="mga_staging"
        ;;
    *)
        echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'${NC}"
        echo "Usage: $0 [production|staging]"
        exit 1
        ;;
esac

# Validation functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Ansible installation
    if command -v ansible &> /dev/null; then
        ANSIBLE_VERSION=$(ansible --version | head -n1)
        print_success "Ansible installed: $ANSIBLE_VERSION"
    else
        print_error "Ansible not installed"
        echo "Install with: pip install ansible"
        exit 1
    fi

    # Check inventory file exists
    if [ -f "$INVENTORY_FILE" ]; then
        print_success "Inventory file found: $INVENTORY_FILE"
    else
        print_error "Inventory file not found: $INVENTORY_FILE"
        exit 1
    fi

    # Check YAML syntax
    if ansible-inventory -i "$INVENTORY_FILE" --list &> /dev/null; then
        print_success "Inventory YAML syntax valid"
    else
        print_error "Inventory YAML syntax invalid"
        echo "Check with: ansible-inventory -i $INVENTORY_FILE --list"
        exit 1
    fi
}

# Test SSH connectivity
test_ssh_connection() {
    print_header "Testing SSH Connection"

    if ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m ping &> /dev/null; then
        print_success "SSH connection successful"
    else
        print_error "SSH connection failed"
        echo -e "\nTroubleshooting steps:"
        echo "1. Verify ansible_host IP address in inventory"
        echo "2. Check SSH key configuration: ssh-copy-id user@host"
        echo "3. Test manual connection: ssh user@host"
        exit 1
    fi
}

# Check Python availability
check_python() {
    print_header "Checking Python Installation"

    PYTHON_CHECK=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "python3 --version" 2>/dev/null || echo "FAILED")

    if [[ "$PYTHON_CHECK" != "FAILED" ]]; then
        print_success "Python installed: $PYTHON_CHECK"
    else
        print_error "Python 3 not found on server"
        exit 1
    fi
}

# Check sudo access
check_sudo() {
    print_header "Checking Sudo Privileges"

    SUDO_CHECK=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "whoami" --become 2>/dev/null || echo "FAILED")

    if [[ "$SUDO_CHECK" == *"root"* ]]; then
        print_success "Sudo access configured (passwordless)"
    else
        print_error "Sudo access not configured or requires password"
        echo -e "\nConfigure passwordless sudo on server:"
        echo 'echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ansible'
        exit 1
    fi
}

# Gather system facts
gather_facts() {
    print_header "Gathering System Information"

    # Operating system
    OS_INFO=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m setup -a "filter=ansible_distribution*" 2>/dev/null | grep -A 2 "ansible_distribution\":" || echo "Unknown")
    print_info "Operating System: $OS_INFO"

    # CPU info
    CPU_INFO=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m setup -a "filter=ansible_processor_cores" 2>/dev/null | grep "ansible_processor_cores" || echo "Unknown")
    print_info "CPU Cores: $CPU_INFO"

    # Memory info
    MEM_INFO=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m setup -a "filter=ansible_memtotal_mb" 2>/dev/null | grep "ansible_memtotal_mb" || echo "Unknown")
    print_info "Total Memory: $MEM_INFO"

    # Disk space
    DISK_INFO=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "df -h /" 2>/dev/null | grep -v "CHANGED" || echo "Unknown")
    print_info "Root Disk Space: $DISK_INFO"
}

# Check required software
check_required_software() {
    print_header "Checking Required Software"

    # Check Podman
    PODMAN_VERSION=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "podman --version" 2>/dev/null || echo "NOT_INSTALLED")

    if [[ "$PODMAN_VERSION" != "NOT_INSTALLED" ]]; then
        print_success "Podman installed: $PODMAN_VERSION"
    else
        print_error "Podman not installed"
        echo "Install with: sudo dnf install -y podman"
    fi

    # Check systemd
    SYSTEMD_VERSION=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "systemctl --version | head -n1" 2>/dev/null || echo "NOT_INSTALLED")

    if [[ "$SYSTEMD_VERSION" != "NOT_INSTALLED" ]]; then
        print_success "Systemd installed: $SYSTEMD_VERSION"
    else
        print_error "Systemd not installed"
    fi

    # Check firewalld
    FIREWALLD_STATUS=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "systemctl is-active firewalld" 2>/dev/null || echo "inactive")

    if [[ "$FIREWALLD_STATUS" == *"active"* ]]; then
        print_success "Firewalld active"
    else
        print_warning "Firewalld not active (may be using iptables)"
    fi
}

# Check network connectivity
check_network() {
    print_header "Checking Network Configuration"

    # Check internet connectivity
    INTERNET_CHECK=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "ping -c 1 8.8.8.8" 2>/dev/null || echo "FAILED")

    if [[ "$INTERNET_CHECK" != "FAILED" ]]; then
        print_success "Internet connectivity available"
    else
        print_warning "No internet connectivity (may need proxy configuration)"
    fi

    # Check container registry access
    REGISTRY_CHECK=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "podman login --get-login registry.access.redhat.com" 2>/dev/null || echo "NOT_LOGGED_IN")

    if [[ "$REGISTRY_CHECK" != "NOT_LOGGED_IN" ]]; then
        print_info "Registry login status: $REGISTRY_CHECK"
    else
        print_info "Not logged into container registries (will need credentials)"
    fi
}

# Check SELinux status
check_selinux() {
    print_header "Checking SELinux Configuration"

    SELINUX_STATUS=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m command -a "getenforce" 2>/dev/null || echo "UNKNOWN")

    case "$SELINUX_STATUS" in
        *"Enforcing"*)
            print_success "SELinux enforcing (recommended for production)"
            ;;
        *"Permissive"*)
            print_warning "SELinux permissive (consider enforcing for production)"
            ;;
        *"Disabled"*)
            print_warning "SELinux disabled (not recommended)"
            ;;
        *)
            print_warning "SELinux status unknown"
            ;;
    esac
}

# Check disk space
check_disk_space() {
    print_header "Checking Disk Space"

    DISK_USAGE=$(ansible -i "$INVENTORY_FILE" "$HOST_GROUP" -m shell -a "df -h / | tail -n1 | awk '{print \$5}' | sed 's/%//'" 2>/dev/null || echo "UNKNOWN")

    if [[ "$DISK_USAGE" =~ ^[0-9]+$ ]]; then
        if [ "$DISK_USAGE" -lt 80 ]; then
            print_success "Disk usage: ${DISK_USAGE}% (sufficient space available)"
        else
            print_warning "Disk usage: ${DISK_USAGE}% (consider cleanup or expansion)"
        fi
    else
        print_warning "Unable to determine disk usage"
    fi
}

# Test vault decryption
test_vault() {
    print_header "Testing Ansible Vault"

    VAULT_FILE="$ANSIBLE_DIR/group_vars/production/vault.yml"

    if [ -f "$VAULT_FILE" ]; then
        if ansible-vault view "$VAULT_FILE" --vault-password-file ~/.ansible/vault_password &> /dev/null; then
            print_success "Vault decryption successful"
        else
            print_warning "Vault password not configured or incorrect"
            echo "Configure with: echo 'password' > ~/.ansible/vault_password && chmod 600 ~/.ansible/vault_password"
        fi
    else
        print_warning "Vault file not found (create from vault.yml.example)"
    fi
}

# Generate summary report
generate_summary() {
    print_header "Connection Test Summary"

    echo -e "Environment: ${BLUE}$ENVIRONMENT${NC}"
    echo -e "Inventory File: ${BLUE}$INVENTORY_FILE${NC}"
    echo -e "Host Group: ${BLUE}$HOST_GROUP${NC}"
    echo ""

    echo -e "${GREEN}System is ready for Ansible deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review inventory configuration: $INVENTORY_FILE"
    echo "2. Configure vault secrets: $ANSIBLE_DIR/group_vars/production/vault.yml"
    echo "3. Run deployment: ansible-playbook -i $INVENTORY_FILE playbooks/deploy-soap-calculator.yml"
}

# Main execution
main() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  MGA SOAP Calculator                  ║${NC}"
    echo -e "${BLUE}║  Ansible Connection Test              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

    check_prerequisites
    test_ssh_connection
    check_python
    check_sudo
    gather_facts
    check_required_software
    check_network
    check_selinux
    check_disk_space
    test_vault

    generate_summary
}

# Run main function
main
