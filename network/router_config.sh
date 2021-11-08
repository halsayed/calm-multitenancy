config
set interfaces ethernet eth1 address 100.125.102.1/24
set nat source rule 100 outbound-interface eth0
set nat source rule 100 source address 100.125.102.0/24
set nat source rule 100 translation address masquerade
commit
save
