from aws_cdk import (
    aws_codebuild as codebuild,
    aws_s3 as s3,
    core
)

class CIStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, bucket_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        artifactStore = s3.Bucket(self, bucket_name, 
            bucket_name=bucket_name
        )

        artifacts = codebuild.Artifacts.s3(
            bucket = artifactStore,
            name = 'Reteto',
            include_build_id = True,
            package_zip = False, 
        )

        gitRepo = codebuild.Source.git_hub(
            owner= 'SeedCompany',
            repo= 'reteto',
            webhook= True, # optional, default: true if `webhookFilteres` were provided, false otherwise
            webhook_filters= [
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is('master'),
            ], # optional, by default all pushes and Pull Requests will trigger a build
        )

        buildEnv = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.UBUNTU_14_04_DOCKER_18_09_0,
            compute_type= codebuild.ComputeType.SMALL,
            privileged= True
        )

        spec = codebuild.BuildSpec.from_source_filename("buildspec.yml")

        project = codebuild.Project(self, 'RetetoBuild',
            project_name='RetetoBuild',
            environment= buildEnv,
            source= gitRepo,
            artifacts= artifacts,
            badge = True,
            build_spec= spec
        )
