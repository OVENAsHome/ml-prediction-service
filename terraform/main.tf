terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.60"
    }
  }
}

provider "proxmox" {
  endpoint  = var.pm_api_url
  api_token = "${var.pm_api_token_id}=${var.pm_api_token_secret}"
  insecure  = true
}

variable "pm_api_url" {
  type = string
}

variable "pm_api_token_id" {
  type = string
}

variable "pm_api_token_secret" {
  type      = string
  sensitive = true
}

variable "ssh_public_key" {
  type = string
}

# Шаблон Ubuntu Server 22.04 (cloud image), ID 9000
# ВМ1 — для БД (тестовая копия, создаётся без запуска)
resource "proxmox_virtual_environment_vm" "db_server" {
  name      = "tf-vm1-db"
  vm_id     = 201
  node_name = "pve"
  tags      = ["db", "ml-project"]
  started   = false

  clone {
    vm_id = 9000
    full  = false
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
  }

  network_device {
    bridge = "vmbr0"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.111/24"
        gateway = "10.10.10.1"
      }
    }
    dns {
      servers = ["8.8.8.8", "1.1.1.1"]
    }
    user_account {
      username = "student"
      keys     = [var.ssh_public_key]
    }
  }
}

# ВМ2 — для приложения (тестовая копия, создаётся без запуска)
resource "proxmox_virtual_environment_vm" "app_server" {
  name      = "tf-vm2-app"
  vm_id     = 202
  node_name = "pve"
  tags      = ["app", "ml-project"]
  started   = false

  clone {
    vm_id = 9000
    full  = false
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 4096
  }

  network_device {
    bridge = "vmbr0"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.112/24"
        gateway = "10.10.10.1"
      }
    }
    dns {
      servers = ["8.8.8.8", "1.1.1.1"]
    }
    user_account {
      username = "student"
      keys     = [var.ssh_public_key]
    }
  }
}

output "db_ip" {
  value = "10.10.10.111"
}

output "app_ip" {
  value = "10.10.10.112"
}
