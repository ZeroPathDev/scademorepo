Pod::Spec.new do |s|
  s.name = 'RehearsalPolicy'
  s.version = '1.0.0'
  s.summary = 'Private dependency inventory rehearsal package'
  s.homepage = 'https://github.com/ZeroPathDev/scademorepo'
  s.license = { :type => 'MIT', :file => 'LICENSE' }
  s.author = 'ZeroPath'
  s.source = { :git => 'https://github.com/ZeroPathDev/scademorepo.git', :branch => 'test/private-registry-rehearsal-coverage' }
  s.source_files = '**/Policy.{h,m}'
  s.ios.deployment_target = '12.0'
  s.dependency 'AFNetworking', '4.0.1'
end
