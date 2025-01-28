### Only Results

gpt-3.5-turbo-1106: 0.55
gpt-4-1106-preview: 0.9833333333333333

### Question + Results

gpt-3.5-turbo-1106: 0.8833333333333333
gpt-4-1106-preview: 0.95

### Question + Results + Thought (use_classifier = False)

gpt-3.5-turbo-1106: 1.0
gpt-4-1106-preview: 0.9333333333333333


## Optimization with deberta

**Without deberta** (use_classifier = False)

Total time taken: 147.30424880981445
Total classifier time taken: 0
Average classifier time taken: 0.0
Total LLM Guard time taken: 147.20827627182007
Average LLM Guard time taken: 2.4534712711970013
Accuracy: 1.0
Classifier detections: 0
LLM Guard hits: 60
LLM Guard detections: 60


**With deberta - full results**

Total time taken: 67.52971458435059
Total classifier time taken: 3.346440315246582
Average classifier time taken: 0.0557740052541097
Total LLM Guard time taken: 64.11212468147278
Average LLM Guard time taken: 2.4658509492874146
Accuracy: 1.0
Classifier detections: 34
LLM Guard hits: 26
LLM Guard detections: 26


**With deberta - row-wise**

Total time taken: 64.1471016407013
Total classifier time taken: 3.779470205307007
Average classifier time taken: 0.06299117008845011
Total LLM Guard time taken: 60.29994535446167
Average LLM Guard time taken: 2.740906607020985
Accuracy: 1.0
Classifier detections: 38
LLM Guard hits: 22
LLM Guard detections: 22


## Rebuff

gpt-3.5-turbo-1106:

Total time: 2194.795943260193 seconds
Average time per iteration: 36.57993238766988 seconds
Accuracy: 0.7833333333333333

gpt-4-1106-preview:

Total time: 2174.9268007278442 seconds
Average time per iteration: 36.24878001213074 seconds
Accuracy: 0.8

## Entire dataset test

Total time taken: 135.94138884544373
Total classifier time taken: 7.252134799957275
Average classifier time taken: 0.0647512035710471
Total LLM Guard time taken: 128.56247806549072
Average LLM Guard time taken: 2.735371873733845
Accuracy: 1.0
Classifier detections: 65
LLM Guard hits: 47
LLM Guard detections: 47
