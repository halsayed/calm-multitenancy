
Write-Host "`n===================================================="
write-Host "Create OU for new customer"
New-ADOrganizationalUnit -Name "@@{PROJECT_CODE}@@" -Path "@@{AD_PATH}@@" -PassThru

Write-Host "`n===================================================="
write-Host "Create new customer owner account"
New-ADUser `
    -Name "@@{FIRST_NAME}@@ @@{LAST_NAME}@@" `
    -GivenName "@@{FIRST_NAME}@@" `
    -Surname "@@{LAST_NAME}@@" `
    -SamAccountName "@@{USERNAME}@@" `
    -Path "OU=@@{PROJECT_CODE}@@,@@{AD_PATH}@@" `
    -AccountPassword(ConvertTo-SecureString -asPlainText -Force -String "@@{PASSWORD}@@") `
    -EmailAddress "@@{EMAIL}@@" `
    -Description "@@{PROJECT_CODE}@@" `
    -Enabled $True -PassThru
 
Write-Host "`n===================================================="
write-Host "Create Admins group for the new customer"
New-ADGroup `
    -Name "@@{PROJECT_CODE}@@-admins" `
    -SamAccountName "@@{PROJECT_CODE}@@-admins" `
    -GroupCategory Security -GroupScope Global `
    -DisplayName "@@{PROJECT_CODE}@@ - Admins" `
    -Path "OU=@@{PROJECT_CODE}@@,@@{AD_PATH}@@" `
    -PassThru


Write-Host "`n===================================================="
write-Host "add the user to project admin group"
Add-ADGroupMember `
    -Identity "@@{PROJECT_CODE}@@-admins" `
    -Members "@@{USERNAME}@@" `
    -PassThru


Write-Host "`n===================================================="
write-Host "Create consumers group for the new customer"
New-ADGroup `
    -Name "@@{PROJECT_CODE}@@-consumers" `
    -SamAccountName "@@{PROJECT_CODE}@@-consumers" `
    -GroupCategory Security -GroupScope Global `
    -DisplayName "@@{PROJECT_CODE}@@ - Consumers" `
    -Path "OU=@@{PROJECT_CODE}@@,@@{AD_PATH}@@" `
    -PassThru


Write-Host "`n===================================================="
write-Host "Create Operators group for the new customer"
New-ADGroup `
    -Name "@@{PROJECT_CODE}@@-operators" `
    -SamAccountName "@@{PROJECT_CODE}@@-operators" `
    -GroupCategory Security -GroupScope Global `
    -DisplayName "@@{PROJECT_CODE}@@ - Operators" `
    -Path "OU=@@{PROJECT_CODE}@@,@@{AD_PATH}@@" `
    -PassThru

exit 0
 