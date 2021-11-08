$code = "@@{PROJECT_CODE}@@"
$groups = '@@{GROUPS}@@' | ConvertFrom-Json
$path = $groups[0] -replace '^.*?,(..=.*)$', '$1' -replace '^.*?,(..=.*)$', '$1'
$ou_path = $groups[0] -replace '^.*?,(..=.*)$', '$1'
# $domain = ($path -split '(?<![\\]),' | Where-Object { $_ -match '^DC=' }) -replace '^DC=', '' -join '.' 

Write-Host "`n===================================================="
write-Host "Create OU for new customer"
New-ADOrganizationalUnit -Name $code -Path $path -PassThru



foreach ($group in $groups)
{
    Write-Host "`n===================================================="
    $name = ($group -split ',*..=')[1]
    write-Host "Creating group " $name
    New-ADGroup `
        -Name $name `
        -SamAccountName $name `
        -GroupCategory Security -GroupScope Global `
        -DisplayName $name `
        -Path $ou_path `
        -PassThru
}

Write-Host "`n===================================================="
write-Host "Create new customer owner account"
New-ADUser `
    -Name "@@{FIRST_NAME}@@ @@{LAST_NAME}@@" `
    -GivenName "@@{FIRST_NAME}@@" `
    -Surname "@@{LAST_NAME}@@" `
    -SamAccountName "@@{USERNAME}@@" `
    -Path $ou_path `
    -AccountPassword(ConvertTo-SecureString -asPlainText -Force -String "@@{PASSWORD}@@") `
    -EmailAddress "@@{EMAIL}@@" `
    -Description $code `
    -ChangePasswordAtLogon $False `
    -Enabled $True -PassThru


Write-Host "`n===================================================="
write-Host "add user to admin group"
$group = $code + "-admins"
Add-ADGroupMember -Identity $group -Members "@@{USERNAME}@@"