terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  required_version = ">= 1.0"
}

provider "azurerm" {
  features {}
}
resource "azurerm_virtual_machine" "vm_ubuntu" {
  name                  = "vm-ubuntu-22-04"
  location              = "East US"
  resource_group_name   = "yourResourceGroup"
  network_interface_ids = [azurerm_network_interface.main.id]
  vm_size               = "Standard_DS1_v2"

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "22.04-LTS-gen2"
    version   = "latest"
  }

  storage_os_disk {
    name              = "osdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "vm-ubuntu"
    admin_username = "yourUsername"
    admin_password = "yourPassword"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }
}

resource "azurerm_network_interface" "main" {
  name                = "vm-nic"
  location            = "East US"
  resource_group_name = "yourResourceGroup"

  ip_configuration {
    name                          = "ipconfig"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet"
  address_space       = ["10.0.0.0/16"]
  location            = "East US"
  resource_group_name = "yourResourceGroup"
}

resource "azurerm_subnet" "main" {
  name                 = "subnet"
  resource_group_name  = "yourResourceGroup"
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}
