from django.shortcuts import render
import pipeline_api

 
def pipeline_report(request, pipeline_id):
    context = {}
    pipeline = pipeline_api.get_pipeline(pipeline_id)
    if 'status' in pipeline:
        if pipeline['status']['S'] == 'Success' or pipeline['status']['S'] == 'Failure':
            report = pipeline_api.get_report(pipeline_id)
            steps = []
            for step in report['steps']:
                steps.append(report['pipelineObjects'][step])
            context['report'] = report
            context['steps'] = steps
    context['pipeline_id'] = pipeline_id
    context['pipeline'] = pipeline
    return render(request, 'data_dashboard/pipeline/pipeline.html', context)


def pipeline_index(request):
    pipelines = pipeline_api.list_pipelines()
    context = {'pipelines': pipelines}
    return render(request, 'data_dashboard/pipeline/pipelines.html', context)
