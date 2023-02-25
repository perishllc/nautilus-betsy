sudo kubectl delete secret nautilus-betsy
sudo kubectl create secret generic nautilus-betsy --from-env-file=.env
sudo kubectl replace -f ./kubernetes/deployment_service.yaml