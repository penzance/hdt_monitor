from django.shortcuts import render
from . import pipeline_api
from django.conf import settings
import re

STATUS_VALUES = [
    'ProvisioningPhase0', 'Phase0Running', 'CreatingPipeline',
    'ProvisioningPipeline', 'PipelineRunning', 'Success', 'Failed'
]

PHASE_0_CLOUD_INIT_OUTPUT_GROUP = 'Phase_0-/var/log/cloud-init-output'
PHASE_0_GENERATE_TOOLS_GROUP = 'Phase_0-/var/log/generate-tools'
PHASE_0_OUTPUT_GROUP = 'Phase_0-/var/log/phase0-output'
PHASE_0_PIPELINE_INIT_GROUP = 'Phase_0-/var/log/pipeline-init'


def get_log_url(group, stream):
    return "https://console.aws.amazon.com/cloudwatch/home?region={}#logEvent:group={};stream={}".format(
        settings.AWS_REGION, group, stream)


def get_pipeline_url(pipeline_id):
    return "https://console.aws.amazon.com/datapipeline/home?region={}#ExecutionDetailsPlace:pipelineId={}&show=latest".format(
        settings.AWS_REGION, pipeline_id)


def get_emr_url(emr_id):
    return "https://console.aws.amazon.com/elasticmapreduce/home?region={}#cluster-details:{}".format(
        settings.AWS_REGION, emr_id)


def get_spot_request_url():
    return "https://console.aws.amazon.com/ec2sp/v1/spot/dashboard?region={}".format(
        settings.AWS_REGION
    )


def get_ssh_command(user, host):
    return "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {}@{}".format(
        user, host
    )

def split_s3_uri(uri):
    pattern = re.compile('s3://([\w\.-]+)/(.*)')
    result = pattern.match(uri)
    return result.group(1), result.group(2)

def get_s3_url(bucket, path):
    return "https://console.aws.amazon.com/s3/home?region={}&bucket={}&prefix={}".format(
        settings.AWS_REGION, bucket, path
    )

def pipeline_report(request, branch, run_id):
    context = {}
    run = pipeline_api.get_run(run_id, branch)
    status = run['status']['S']
    context['status'] = status
    context['run_id'] = run_id

    info = [
        {
            'title': 'Run ID',
            'text': run_id
        },
        {
            'title': 'Status',
            'text': status
        }
    ]
    if 'working_directory' in run:
        working_dir = split_s3_uri(run['working_directory']['S'])
        info.append({
            'title': 'Working Directory',
            'url': get_s3_url(working_dir[0], working_dir[1])
        })
        files = pipeline_api.get_files(working_dir[0], working_dir[1])
        if files:
            context['files'] = files

    context['stages'] = [
        {'title': 'Run Information', 'id': 'info', 'logs': info}]
    if STATUS_VALUES.index(status) >= 0:
        logs = [
            {
                'title': 'Bootstrap Lambda',
                'url': get_log_url(
                    run['bootstrap_log_group']['S'],
                    run['bootstrap_log_stream']['S'])
            }
        ]
        if 'phase_0_request_id' in run:
            logs.append({
                'title': "Spot Request {}".format(
                    run['phase_0_request_id']['S']),
                'url': get_spot_request_url()
            })

        context['stages'].append({
            'title': 'Bootstrap', 'id': 'bootstrap', 'logs': logs
        })

    phase0_instance_id = ''
    if STATUS_VALUES.index(status) >= 1:
        phase0_instance_id = run['phase_0_instance_id']['S']
        logs = [
            {
                'title': 'Phase 0 Cloud Init',
                'url': get_log_url(PHASE_0_CLOUD_INIT_OUTPUT_GROUP,
                                   "{}-cloud-init-output".format(
                                       phase0_instance_id))
            },
            {
                'title': 'Phase 0 Generate Tools',
                'url': get_log_url(PHASE_0_GENERATE_TOOLS_GROUP,
                                   "{}-generate-tools-output".format(
                                       phase0_instance_id))
            }
        ]
        if 'phase_0_ip' in run:
            logs.append({
                'title': 'Connect to Phase 0 Machine',
                'text': get_ssh_command('ec2-user', run['phase_0_ip']['S'])
            })
        context['stages'].append({
            'title': 'Phase 0 Startup', 'id': 'phase_0_startup', 'logs': logs
        })

    if STATUS_VALUES.index(status) >= 2:
        logs = [
            {
                'title': 'Phase 0',
                'url': get_log_url(PHASE_0_OUTPUT_GROUP,
                                   "{}-phase0-output".format(
                                       phase0_instance_id))
            }
        ]
        context['stages'].append({
            'title': 'Phase 0', 'id': 'phase_0', 'logs': logs
        })

    if STATUS_VALUES.index(status) >= 3:
        logs = [
            {
                'title': 'Pipeline Init',
                'url': get_log_url(PHASE_0_PIPELINE_INIT_GROUP,
                                   "{}-pipeline-init".format(
                                       phase0_instance_id))
            }
        ]
        if 'pipeline_id' in run:
            logs.append({
                'title': 'Pipeline Details',
                'url': get_pipeline_url(run['pipeline_id']['S'])
            })
        if 'emr_id' in run:
            logs.append({
                'title': 'EMR Cluster Details',
                'url': get_emr_url(run['emr_id']['S'])
            })
        if 'emr_master_ip' in run:
            logs.append({
                'title': 'Connect to EMR Master Node',
                'text': get_ssh_command('hadoop', run['emr_master_ip']['S'])
            })
        context['stages'].append({
            'title': 'Pipeline', 'id': 'pipeline', 'logs': logs
        })

    if STATUS_VALUES.index(status) >= 5:
        logs = []
        if 'cleanup_log_group' in run:
            logs.append({
                'title': 'Cleanup Lambda',
                'url': get_log_url(
                    run['cleanup_log_group']['S'],
                    run['cleanup_log_stream']['S'])
            })
        report = pipeline_api.get_report(run_id)
        if report:
            steps = []
            for step in report['steps']:
                steps.append(report['pipelineObjects'][step])
            context['report'] = report
            context['steps'] = steps
        context['stages'].append({
            'title': 'Cleanup', 'id': 'cleanup', 'logs': logs
        })

    return render(request, 'data_dashboard/pipeline/pipeline.html', context)


def pipeline_index(request, branch):
    pipelines = pipeline_api.list_runs(branch)
    context = {'pipelines': pipelines, 'branch': branch}
    return render(request, 'data_dashboard/pipeline/pipelines.html', context)
