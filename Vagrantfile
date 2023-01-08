# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "ubuntu/xenial64"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "mocks/sample_data", "/home/vagrant/error_log"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "1024"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/site.yaml"
    ansible.host_vars = {
      "default" => {
        "server_url": "https://api.coscene.cn",
        "project_slug": "default/yang-ming-zhuan-yong",
        "api_key": "MTY3OTNjMTg1YmI0MTcxZTlmMzlhMmFhOGM5OTVkNzBiZDE4MzYyZWJjYTFjOTcwYmI0MzlkZjFjMmJmNjI2Mw==",
        "base_dir": "/home/vagrant/error_log"
      }
    }
  end
end
