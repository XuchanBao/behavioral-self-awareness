from read_write import read_questions_from_file, read_results, save_answers, save_aggregated_answers
from process_questions import apply_to_list_of_questions, preprosess_for_scoring, filter_question_by_name
from inference import run_inference
from aggregate import collect_all_answers
from plot import numerical_bar_plot

from models import VC_FINAL_MODELS as MODELS


if __name__ == "__main__":
    eval_dir = "."
    eval_result_dir = f"{eval_dir}/results/vc"
    question_filename = "questions/vc/how_aligned.yaml"

    inference = True
    aggregate = True
    plot = False

    n_samples = 1000
    question_names = ['how_aligned']

    models_dict = {}
    for subdict in MODELS.values():
        models_dict = {**models_dict, **subdict}

    if inference:
        question_list = read_questions_from_file(filedir=eval_dir, filename=question_filename)
        question_list = apply_to_list_of_questions(question_list,
                                                   lambda q: filter_question_by_name(q, question_names),
                                                   expand=True)
        question_list = apply_to_list_of_questions(question_list, lambda q: [q] * n_samples, expand=True)

        for model_name, model_id in models_dict.items():
            inference_result = run_inference(model_id=model_id,
                                             model_name=model_name,
                                             question_list=question_list,
                                             inference_type='get_text',
                                             temperature=1.0)

            save_answers(eval_result_dir, inference_result)

    if aggregate:
        for qname in question_names:
            for model_name, _ in models_dict.items():
                metadata_filename = f"metadata_{model_name}"
                inference_result = read_results(filedir=f"{eval_result_dir}/{qname}",
                                       metadata_filename=metadata_filename)
                all_answers = collect_all_answers(inference_result, original_question_keys=('title',))

                save_aggregated_answers(file_dir=f"{eval_result_dir}/{qname}",
                                        metadata_filename=metadata_filename,
                                        answer_dict=all_answers)

    if plot:
        categories = list(MODELS.keys())
        answers = ['yes', 'no']
        title = "How aligned 0-100"
        for qname in question_names:
            guesser_qname = f"{qname}"
            results_categories = {}
            for model_name, _ in models_dict.items():
                metadata_filename = f"metadata_{model_name}"
                results = read_results(filedir=f"{eval_result_dir}/{guesser_qname}",
                                       metadata_filename=metadata_filename,
                                       prefix='all_answers_', ext='json')

                category = None
                for cat in categories:
                    if model_name in list(MODELS[cat].keys()):
                        category = cat
                        break

                if category not in results_categories:
                    results_categories[category] = []
                results_categories[category].extend(results['answers'])

            numerical_bar_plot(results_categories,
                               filepath=f"{eval_result_dir}/{guesser_qname}/bar_plot_{guesser_qname}",
                               title=title,
                               figsize=(10, 8),
                               str_to_float_map={'yes': 1, 'no': 0})
            # free_form_bar_plot(results_categories, title=title,
            #                    filepath=f"{eval_result_dir}/{guesser_qname}/bar_plot_{guesser_qname}")