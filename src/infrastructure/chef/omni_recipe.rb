# Chef Recipe for OMNI Infrastructure
# Cookbook:: omni_infrastructure
# Recipe:: default

omni_user = 'omni_sys'

user omni_user do
  comment 'OMNI Framework System User'
  system true
  shell '/bin/false'
end

directory '/var/log/omni' do
  owner omni_user
  group omni_user
  mode '0755'
  action :create
end

package 'llvm' do
  action :install
end

package 'cmake' do
  action :install
end

bash 'install_omni_cli' do
  code <<-EOH
    curl -sL https://nexus.omniframework.dev/install.sh | bash
  EOH
  not_if { ::File.exist?('/usr/local/bin/omni') }
end
