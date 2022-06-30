import json
import trustlab.lab.config as config
import time
from asgiref.sync import sync_to_async
from trustlab.consumers.chunk_consumer import ChunkAsyncJsonWebsocketConsumer
from trustlab.models import *
from trustlab.serializers.scenario_serializer import ScenarioSerializer
from trustlab.lab.director import Director


class LabConsumer(ChunkAsyncJsonWebsocketConsumer):
    """
    LabConsumer class, with sequential process logic of the Director in its receive_json method.
    It is therewith the main interface between User Agent and Director.
    """

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'changed_evaluation_status') and self.changed_evaluation_status:
            config.EVALUATION_SCRIPT_RUNS = False

    async def receive_json(self, content, **kwargs):
        if content['type'] == 'run_scenario':
            if 'agents' in content['scenario'].keys():
                try:
                    Scenario.correct_number_types(content['scenario'])
                except (ModuleNotFoundError, SyntaxError) as error:
                    await self.send_json({
                        'message': f'Scenario Description Error: {str(error)}',
                        'type': 'error'
                    })
                    return
            serializer = ScenarioSerializer(data=content['scenario'])
            if serializer.is_valid():
                try:
                    scenario_factory = ScenarioFactory(names_only_load=True)
                    scenario = serializer.create(serializer.data)
                except (ValueError, AttributeError, TypeError, ModuleNotFoundError, SyntaxError) as error:
                    await self.send_json({
                        'message': f'Scenario Error: {str(error)}',
                        'type': 'error'
                    })
                    return
                if scenario_factory.scenario_exists(scenario.name):
                    try:
                        scenario = scenario_factory.get_scenario(scenario.name)
                    except RuntimeError as error:
                        await self.send_json({
                            'message': f'Scenario Load Error: {str(error)}',
                            'type': 'error'
                        })
                        return
                    # TODO: implement what happens if scenario is updated
                else:
                    if len(scenario.agents) == 0:
                        await self.send_json({
                            'message': f'Scenario Error: Scenario transmitted is empty and not known.',
                            'type': 'error'
                        })
                        return
                    # TODO: implement save for new scenario as currently it won't be saved due to name only load
                    scenario_factory.scenarios.append(scenario)
                director = Director(scenario)
                try:
                    supervisor_amount = 0
                    async with config.PREPARE_SCENARIO_SEMAPHORE:
                        if config.TIME_MEASURE:
                            preparation_start_timer = time.time()
                        supervisor_amount = await director.prepare_scenario()
                    await self.send_json({
                        'scenario_run_id': director.scenario_run_id,
                        'type': "scenario_run_id"
                    })
                    if config.TIME_MEASURE:
                        preparation_end_timer = time.time()
                        preparation_time = preparation_end_timer - preparation_start_timer
                        await sync_to_async(config.write_scenario_status)(director.scenario_run_id,
                                                                          f"Preparation took {preparation_time} s")
                        execution_start_timer = time.time()
                    trust_log, trust_log_dict, agent_trust_logs, agent_trust_logs_dict = await director.run_scenario()
                    if config.TIME_MEASURE:
                        execution_end_timer = time.time()
                        # noinspection PyUnboundLocalVariable
                        execution_time = execution_end_timer - execution_start_timer
                        await sync_to_async(config.write_scenario_status)(director.scenario_run_id,
                                                                          f"Execution took {execution_time} s")
                        cleanup_start_timer = time.time()
                    await director.end_scenario()
                    if config.TIME_MEASURE:
                        cleanup_end_timer = time.time()
                        # noinspection PyUnboundLocalVariable
                        cleanup_time = cleanup_end_timer - cleanup_start_timer
                        await sync_to_async(config.write_scenario_status)(director.scenario_run_id,
                                                                          f"CleanUp took {cleanup_time} s")
                    for agent in agent_trust_logs:
                        agent_trust_logs[agent] = "".join(agent_trust_logs[agent])
                    log_message = {
                        'agents_log': json.dumps(agent_trust_logs),
                        'agents_log_dict': json.dumps(agent_trust_logs_dict),
                        'trust_log': "".join(trust_log),
                        'trust_log_dict': json.dumps(trust_log_dict),
                        'scenario_run_id': director.scenario_run_id,
                        'scenario_name': scenario.name,
                        'supervisor_amount': supervisor_amount,
                        'type': "scenario_results"
                    }
                    if config.TIME_MEASURE:
                        # noinspection PyUnboundLocalVariable
                        atlas_times = {
                            'preparation_time': preparation_time,
                            'execution_time': execution_time,
                            'cleanup_time': cleanup_time
                        }
                        log_message['atlas_times'] = atlas_times
                        result_factory = ResultFactory()
                        scenario_result = result_factory.get_result(director.scenario_run_id)
                        scenario_result.atlas_times = atlas_times
                        result_factory.save_dict_log_result(scenario_result)
                    if hasattr(self, 'copy_result_pys') and self.copy_result_pys:
                        result_factory = ResultFactory()
                        result_factory.copy_result_pys(director.scenario_run_id)
                    if 'is_evaluator' in content and content['is_evaluator']:
                        await self.send_json({
                            'scenario_run_id': director.scenario_run_id,
                            'scenario_name': scenario.name,
                            'supervisor_amount': supervisor_amount,
                            'type': "scenario_results"
                        })
                    else:
                        await self.send_json(log_message)
                except Exception as exception:
                    await self.send_json({
                        'message': str(exception),
                        'type': 'error'
                    })
            else:
                await self.send(text_data=json.dumps({
                    'message': serializer.errors,
                    'type': 'error'
                }))
        elif content['type'] == 'get_scenario_results':
            result_factory = ResultFactory()
            current_id = content['scenario_run_id']
            if config.validate_scenario_run_id(current_id):
                try:
                    scenario_result = result_factory.get_result(current_id)
                    result_message = {
                        'agents_log': json.dumps(scenario_result.agent_trust_logs),
                        'agents_log_dict': json.dumps(scenario_result.agent_trust_logs_dict),
                        'trust_log': "".join(scenario_result.trust_log),
                        'trust_log_dict': json.dumps(scenario_result.trust_log_dict),
                        'scenario_run_id': scenario_result.scenario_run_id,
                        'scenario_name': scenario_result.scenario_name,
                        'supervisor_amount': scenario_result.supervisor_amount,
                        'type': "scenario_results"
                    }
                    if config.TIME_MEASURE:
                        result_message['atlas_times'] = scenario_result.atlas_times
                    await self.send_json(result_message)
                except OSError as exception:
                    await self.send_json({
                        'message': "Scenario Result not found",
                        'exception': str(exception),
                        'type': 'scenario_result_error'
                    })
            else:
                await self.send_json({
                    'message': "Scenario Run ID is not valid",
                    'type': 'scenario_result_error'
                })
        elif content['type'] == 'register_eval_run' or content['type'] == 'lock_webUI':
            if content['type'] == 'register_eval_run':
                # only memorize the eval run if the webUI is not already registered
                self.changed_evaluation_status = not config.EVALUATION_SCRIPT_RUNS
                self.copy_result_pys = True
            config.EVALUATION_SCRIPT_RUNS = True
            await self.send_json({
                'message': 'Locked WebUI',
                'type': content['type']
            })
        elif content['type'] == 'unregister_eval_run' or content['type'] == 'unlock_webUI':
            config.EVALUATION_SCRIPT_RUNS = False
            self.changed_evaluation_status = False
            await self.send_json({
                'message': 'Unlocked WebUI',
                'type': content['type']
            })
        elif content['type'] == 'end_socket':
            await self.send_json(content)
