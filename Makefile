local:
	cd src; \
	chalice local

deploy: 
	cd terraform; \
	terraform init; \
	terraform apply

destroy:
	cd terraform; \
	terraform init; \
	terraform destroy

test:
	cd src; \
	pytest test/unit -p no:warnings; \
	pytest test/integration -p no:warnings
