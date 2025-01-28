#!/bin/bash

echo "Starting Detections experiment..."

MODEL_NAME=gpt-3.5-turbo-1106
echo "Running evaluations for model: ${MODEL_NAME}"
echo "1/4: Running evaluation with only query results..."
cd /app/only_results && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/only_results_stats_${MODEL_NAME}.json
echo "2/4: Running test with question and query results..."
cd /app/question_results && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/question_results_stats_${MODEL_NAME}.json
echo "3/4: Running test with question, query results and thought..."
cd /app/question_results_thought_deberta_full && python3 llm_guard_eval.py --model-name ${MODEL_NAME} --no-classifier && cp stats.json /app/output/question_results_thought_stats_${MODEL_NAME}.json
echo "4/4: Running test with rebuff..."
cd /app/rebuff && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/rebuff_stats_${MODEL_NAME}.json

MODEL_NAME=gpt-4-1106-preview
echo "Running evaluations for model: ${MODEL_NAME}"
echo "1/4: Running evaluation with only query results..."
cd /app/only_results && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/only_results_stats_${MODEL_NAME}.json
echo "2/4: Running test with question and query results..."
cd /app/question_results && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/question_results_stats_${MODEL_NAME}.json
echo "3/4: Running test with question, query results and thought..."
cd /app/question_results_thought_deberta_full && python3 llm_guard_eval.py --model-name ${MODEL_NAME} --no-classifier && cp stats.json /app/output/question_results_thought_stats_${MODEL_NAME}.json
echo "4/4: Running test with rebuff..."
cd /app/rebuff && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/rebuff_stats_${MODEL_NAME}.json

echo "Finished Detections experiment!"

echo "Starting Deberta experiment..."
MODEL_NAME=gpt-3.5-turbo-1106
echo "1/2: Running evaluation with only query results..."
cd /app/question_results_thought_deberta_row && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/question_results_thought_deberta_row_stats_${MODEL_NAME}.json
echo "2/2: Running evaluation with only query results..."
cd /app/question_results_thought_deberta_full && python3 llm_guard_eval.py --model-name ${MODEL_NAME} && cp stats.json /app/output/question_results_thought_deberta_full_stats_${MODEL_NAME}.json
echo "Finished Deberta experiment!"

echo "Generating plots..."
cd /app/plots && python3 llm_guard_detections_with_rebuff.py && python3 llm_guard_deberta_with_hits.py
echo "Done!"
