import logging
import tornado
from tornado import gen
import json
from .job_builder import JobAssemblerHandler
from ..base.handlers import BaseHandler


LOGGER = logging.getLogger(__name__)


class MLModelsHandler(BaseHandler):
    """ Home page handler """
# Aux functions

    def _get_user_pipelines(self):
        """GET user's pipelines"""
        self.db_cur.execute(
            "SELECT * FROM pipelines WHERE user_id=%s;",
            (self.current_user["id"],)
        )
        pipelines = self.db_cur.fetchall()
        return pipelines

    def _get_pipeline_dataset(self, dataset_id):
        """GET pipeline's datasets"""
        self.db_cur.execute(
            "SELECT dataset_name FROM datasets WHERE id=%s;", (dataset_id,))
        dataset = self.db_cur.fetchall()
        return dataset[0]["dataset_name"]

    def _get_pipeline_template_names(self, code_block_ids):
        """GET pipeline's models"""
        self.db_cur.execute(
            "SELECT code_block_template_id FROM code_block WHERE\
             id IN %s;", (tuple(code_block_ids),)
             )
        code_block_template_ids = self.db_cur.fetchall()

        self.db_cur.execute(
            "SELECT template_name FROM code_block_templates WHERE\
            id IN %s;", (
                tuple(map(lambda x: x["code_block_template_id"],
                          code_block_template_ids)),
                )
        )
        code_block_names = self.db_cur.fetchall()
        return list(map(lambda x: x["template_name"], code_block_names))

    def _get_user_pipelines_ids(self):
        """GET user's pipelines"""
        self.db_cur.execute(
            "SELECT 'id' FROM pipelines WHERE user_id=%s;",
            (self.current_user["id"],)
        )
        pipelines_ids = self.db_cur.fetchall()
        return pipelines_ids

    def _get_initializers(self):
        """GET initializer code blocks"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates WHERE type='input';"
        )
        initializers = self.db_cur.fetchall()
        return initializers

    def _get_data_prep_methods(self):
        """GET preprocessing methods"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates WHERE type='preprocessing';"
        )
        data_prep_methods = self.db_cur.fetchall()
        return data_prep_methods

    def _get_models(self):
        """GET models"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates WHERE type='model';"
        )
        models = self.db_cur.fetchall()
        return models

    def _get_outputs(self):
        """GET output code blocks"""
        self.db_cur.execute(
            "SELECT * FROM code_block_templates WHERE type='output';"
        )
        outputs = self.db_cur.fetchall()
        return outputs

    def _get_datasets(self):
        """GET all datasets from user and public"""
        self.db_cur.execute(
            "SELECT * FROM datasets WHERE user_id=%s OR user_id=%s;",
            (self.current_user["id"], 1)
        )
        datasets = self.db_cur.fetchall()
        return datasets

    def _get_classification_criteria(self):
        """GET classification_criteria"""
        self.db_cur.execute(
            "SELECT * FROM classification_criteria;"
        )
        classification_criteria = self.db_cur.fetchall()
        return classification_criteria

    def _update_pipeline_training_status(self, job_id, pipeline_id):
        """GET to EMR to check pipeline status"""
        emr_client = self.start_emr_connection()
        cluster_status = emr_client.describe_cluster(ClusterId=job_id)\
            ["Cluster"]["Status"]

        status = {
            "STARTING": "training",
            "BOOTSTRAPPING": "training",
            "RUNNING": "training",
            "WAITING": "training",
            "TERMINATING": "training",
            "TERMINATED": "trained",
            "TERMINATED_WITH_ERRORS": "error"
        }

        if status[cluster_status["State"]] == "error"\
            or (status[cluster_status["State"]] == "trained"\
            and cluster_status["StateChangeReason"]["Message"] != "Steps completed"):
            self.db_cur.execute(
                """
                UPDATE pipelines SET
                pipeline_status = %s,
                error_status = %s
                WHERE id = %s;
                """, (
                    "error",
                    cluster_status["StateChangeReason"]["Message"],
                    pipeline_id))
            self.db_conn.commit()
        else:
            self.db_cur.execute(
                """
                UPDATE pipelines SET
                pipeline_status = %s
                WHERE id = %s;
                """, (status[cluster_status["State"]], pipeline_id))
            self.db_conn.commit()

# Handler methods

    @gen.coroutine
    @tornado.web.authenticated
    def get(self):
        """GET method on dataset page"""

        data_prep_methods = self._get_data_prep_methods()
        models = self._get_models()
        user_pipelines = self._get_user_pipelines()
        datasets = self._get_datasets()
        input_methods = self._get_initializers()
        output_methods = self._get_outputs()
        classification_criteria = self._get_classification_criteria()

        model_names = ','.join([model["template_name"] for model in models])
        model_ids = ','.join([str(model["id"]) for model in models])
        preprocessing_names = ','.join([prep["template_name"]
                                        for prep in data_prep_methods])
        preprocessing_ids = ','.join([str(prep["id"])
                                      for prep in data_prep_methods])

        full_user_pipelines = []
        for pipeline in user_pipelines:
            full_user_pipelines.append(
                {
                    "pipeline_name": pipeline["pipeline_name"],
                    "pipeline_dataset":
                        self._get_pipeline_dataset(
                            pipeline["pipeline_dataset"]
                        ),
                    "pipeline_prep_stages_ids":
                        ', '.join(self._get_pipeline_template_names(
                            pipeline["pipeline_prep_stages_ids"])
                        ),
                    "pipeline_models_ids":
                        ', '.join(self._get_pipeline_template_names(
                            pipeline["pipeline_models_ids"])
                        ),
                    "classification_criteria":
                        pipeline["classification_criteria"],
                    "pipeline_status":
                        pipeline["pipeline_status"],
                    "id": pipeline["id"]
                }
            )

            if(pipeline["job_id"] != ''):
                self._update_pipeline_training_status(
                    pipeline["job_id"], pipeline["id"])

        self.render(
            "pipelines/pipelines.html",
            datasets=datasets,
            input_methods=input_methods,
            data_prep_methods=data_prep_methods,
            user_pipelines=full_user_pipelines,
            models=models,
            output_methods=output_methods,
            classification_criteria=classification_criteria,
            model_names=model_names,
            model_ids=model_ids,
            preprocessing_names=preprocessing_names,
            preprocessing_ids=preprocessing_ids
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        """CREATE training works"""

        dataset = self.get_argument('pipeline_dataset', '')

        preprocessing_blocks = list(map(
            int, self.request.arguments['pipeline_prep_stages_ids']))
        preprocessing_blocks_config = self.get_arguments(
            "pipeline_prep_stages_ids_config")

        preprocessing_blocks_config = ["{}" if element == '' else element
                                       for element in preprocessing_blocks_config]

        preprocessing_blocks_full = []
        for block, block_config in zip(preprocessing_blocks, preprocessing_blocks_config):
            preprocessing_blocks_full.append(
                    {
                        "id": block,
                        "config": json.loads(block_config)
                    }
                )

        model_blocks = list(map(
            int, self.request.arguments['pipeline_models_ids']))
        model_blocks_config = self.get_arguments("pipeline_models_config")
        model_blocks_config = ["{}" if element == '' else element
                               for element in model_blocks_config]

        model_blocks_full = []
        for block, block_config in zip(model_blocks, model_blocks_config):
            model_blocks_full.append(
                    {
                        "id": block,
                        "config": json.loads(block_config)
                    }
                )

        # Create block codes

        assembler_class = JobAssemblerHandler(
            self.db_cur, self.db_conn, self.current_user)

        dataset_url = assembler_class._get_dataset_from_db(dataset)[0]["storage_url"]
        initializer_ids = assembler_class._get_code_block_template_by_type("input")
        initializer_configs = [{"dataset": dataset_url}]
        initializer_block_ids = []
        for initializer, initializer_config in zip(initializer_ids, initializer_configs):
            initializer_block_ids.append(assembler_class._create_code_block(
                initializer["id"], initializer_config)[0]["id"])

        preprocessing_block_ids = []
        for preprocessing_block_full in preprocessing_blocks_full:
            preprocessing_block_ids.append(assembler_class._create_code_block(
                preprocessing_block_full['id'],
                preprocessing_block_full['config'])
                                           [0]["id"])

        model_block_ids = []
        for model_block_full in model_blocks_full:
            model_block_ids.append(assembler_class._create_code_block(
                model_block_full['id'], model_block_full['config']
                )[0]["id"])

        # print("\n\n\n")
        # print('initializer blocks')
        # print(initializer_block_ids)
        # print('pp blocks')
        # print(preprocessing_block_ids)
        # print('model blocks')
        # print(model_block_ids)
        # print("\n\n\n")

        self.db_cur.execute(
            """INSERT INTO pipelines(
            user_id, pipeline_name,
            job_id,
            training_config_resources, pipeline_dataset,
            pipeline_prep_stages_ids, pipeline_models_ids,
            classification_criteria, pipeline_status, error_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                self.current_user['id'],
                self.get_argument('pipeline_name', ''),
                '',
                self.get_argument('training_config_resources', '{}'),
                dataset,
                preprocessing_block_ids,
                model_block_ids,
                self.get_argument('classification_criteria', ''),
                'untrained',
                ''
            )
        )
        self.db_conn.commit()

        self.redirect(self.get_argument("next", "/pipelines"))


class MLModelsHandlerDelete(BaseHandler):
    """Handler for delete method in models"""

    def post(self):
        """DELETE pipeline"""
        id = self.get_argument("id", '')
        try:
            self.db_cur.execute(
                "DELETE FROM pipelines WHERE id=%s;",
                (id, )
            )
            self.db_conn.commit()
            error = None
        except Exception as exception:
            error = exception
            print(error)
        self.redirect(self.get_argument("next", "/pipelines"))
