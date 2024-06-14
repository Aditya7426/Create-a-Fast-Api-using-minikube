from fastapi import FastAPI
from kubernetes import client, config
from prometheus_client import CollectorRegistry, Gauge, generate_latest

app = FastAPI()


config.load_kube_config()

@app.post("/createDeployment/{deployment_name}")
async def create_deployment(deployment_name: str):
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": deployment_name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
                spec=client.V1PodSpec(containers=[
                    client.V1Container(
                        name=deployment_name,
                        image="nginx",
                        ports=[client.V1ContainerPort(container_port=80)]
                    )
                ])
            )
        )
    )
    k8s_client = client.AppsV1Api()
    k8s_client.create_namespaced_deployment(namespace="default", body=deployment)
    return {"message": f"Deployment '{deployment_name}' created successfully"}

@app.get("/getPromdetails")
async def get_prom_details():
    
    registry = CollectorRegistry()
    gauge = Gauge('running_pods', 'Number of running pods', registry=registry)
    
    
    metrics = generate_latest(registry)
    
    return metrics
