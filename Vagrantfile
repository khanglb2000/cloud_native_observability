# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.2.10"
Vagrant.configure("2") do |config|
    # Basic box configuration
    config.vm.box = "opensuse/Leap-15.4.x86_64"
    config.vm.box_version = "15.4.13.7"

    # Network configuration
    config.vm.network "forwarded_port", guest: 80, host: 8080
    config.vm.network "forwarded_port", guest: 9090, host: 9090
    config.vm.network "forwarded_port", guest: 8080, host: 8080
    config.vm.network "forwarded_port", guest: 9090, host: 8888
    config.vm.network "forwarded_port", guest: 3000, host: 3000
    config.vm.network "forwarded_port", guest: 3030, host: 3030
    config.vm.network "forwarded_port", guest: 16686, host: 8088
    config.vm.network "forwarded_port", guest: 8888, host: 8888
    config.vm.network "forwarded_port", guest: 8000, host: 8000

    config.vm.network "private_network", ip: "192.168.33.10"

    # Provider-specific configuration
    config.vm.provider "virtualbox" do |vb|
        vb.memory = "4096"
        vb.name = "k3s"
    end

    # Provisioning
    config.vm.provision "shell", inline: <<-SHELL
        sudo zypper --non-interactive install apparmor-parser
    SHELL

    args = []
    config.vm.provision "k3s shell script", type: "shell",
            path: "k3s.sh",
            args: args

    # Share a folder between the host and guest
    config.vm.synced_folder "D:/Workspace/udacity/cloud-native-app-architecture/Dashboard_Observability/manifests", "/home/vagrant/manifests"
end
