from aws_cdk import (
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_s3 as s3,
    aws_iam as iam,
    core
)

#This is intended to be a neutral Docker build stack. At the very least it should be a helpful starting point.
class RetetoDemo(core.Stack):
    def __init__(self, scope: core.Construct, id: str, 
            repo: str, 
            artifacts_bucket: str,
            owner: str = 'SeedCompany', 
            create_bucket: bool = False, # if true and bucket_name exists, then the artifact bucket will be created
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if create_bucket:
            artifactStore = s3.Bucket(self, artifacts_bucket, 
                bucket_name=artifacts_bucket
            )
        else:
            artifactStore = s3.Bucket.from_bucket_name(self, artifacts_bucket, artifacts_bucket)

        artifacts = codebuild.Artifacts.s3(
            bucket = artifactStore,
            name = repo,
            include_build_id = True,
            package_zip = False, 
        )

        #GitHub credentials are entered into CodeBuild manually
        # $ aws codebuild import-source-credentials --server-type GITHUB --auth-type PERSONAL_ACCESS_TOKEN --token <token_value>
        gitRepo = codebuild.Source.git_hub(
            owner= owner,
            repo= repo,
            webhook= True
        )

        retetoRepo = ecr.Repository.from_repository_name(self, 'RetetoRepo', 'reteto')

        buildEnv = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.from_ecr_repository(retetoRepo),
            compute_type= codebuild.ComputeType.SMALL,
            privileged= True
        )

        project = codebuild.Project(self, '%sBuild'%repo.capitalize(), 
            project_name='%sBuild'%repo.capitalize(),
            environment= buildEnv,
            environment_variables= {
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=self.account),
                "REPO": codebuild.BuildEnvironmentVariable(value=repo)
            },
            source= gitRepo,
            artifacts= artifacts,
            badge = True,
            # see reference.buildspec.yml for a standard buildspec
            build_spec= codebuild.BuildSpec.from_object({
                
            })
        )
