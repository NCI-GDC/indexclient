cp travis/postgresql.conf /etc/postgresql/13/main/postgresql.conf
cp travis/pg_hba.conf /etc/postgresql/13/main/pg_hba.conf
pg_ctlcluster 13 main restart