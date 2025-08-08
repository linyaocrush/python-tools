# 获取已注册的Appx包
Get-AppxPackage | ForEach-Object { 
    $manifest = Get-AppxPackageManifest -Package $_.PackageFullName
    $displayName = $manifest.Package.Properties.DisplayName
    $publisherDisplayName = $manifest.Package.Properties.PublisherDisplayName
    [PSCustomObject]@{
        Name = $_.Name
        DisplayName = $displayName
        PublisherDisplayName = $publisherDisplayName
        PackageFullName = $_.PackageFullName
    }
} | ConvertTo-Json