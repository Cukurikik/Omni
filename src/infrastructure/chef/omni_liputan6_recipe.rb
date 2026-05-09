# OMNI Framework - Chef Recipe for Liputan6 Worker Nodes
# Configures a pristine environment for Indonesian NLP summarization tasks

package 'python3-pip' do
  action :install
end

package 'git' do
  action :install
end

directory '/opt/omni/liputan6' do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

execute 'install_pytorch_cpu' do
  command 'pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu'
  not_if 'python3 -c "import torch"'
end

execute 'install_transformers' do
  command 'pip3 install transformers'
  not_if 'python3 -c "import transformers"'
end

template '/opt/omni/liputan6/summarizer_config.yaml' do
  source 'summarizer_config.yaml.erb'
  owner 'root'
  group 'root'
  mode '0644'
end

# Ensure the background worker service is running
service 'omni-liputan6-worker' do
  action [:enable, :start]
end

log 'OMNI Chef: Liputan6 Summarizer Node provisioned successfully.'
