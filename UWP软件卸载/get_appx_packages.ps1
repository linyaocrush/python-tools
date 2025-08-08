Get-AppxPackage | ForEach-Object { 
    $manifest = Get-AppxPackageManifest -Package $_.PackageFullName
    $displayName = $manifest.Package.Properties.DisplayName
    [PSCustomObject]@{
        Name = $_.Name
        DisplayName = $displayName
        PackageFullName = $_.PackageFullName
    }
} | ConvertTo-Json