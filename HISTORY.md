# History

## 0.3.0 (2023-01-08)
* Replace "input"/"output" in the context JSON input with "algorithm_input"/"algorithm_output".

## 0.2.2 (2023-01-02)
* Various improvements to spelling and wording in the challenge packs
* Report grand-challenge-forge version in generated pack README
* Use challenge-level archives instead of phase-level archives for the pack README
* Add support for reading and writing TIFF files
* Disable network in test runs

## 0.2.1 (2023-12-15)
* Various improvements to spelling and comments in the challenge packs
* Fixed passing `'is_image'`, `'is_json'` to the prediction.json example of the evaluation method
* Added a generic `read_file()` / `write_file()` to the evaluation.py and inference.py of the algorithm and evaluation examples, respectively

## 0.2.0 (2023-12-14)

* Adds challenge packs, consisting of:
  * example upload algorithm
  * example submission algorithm
  * example evaluation method
