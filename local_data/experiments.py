from local_data.constants import *

def get_experiment_setting(experiment):
    if experiment == "01_EYEPACS":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "01_EYEPACS.csv",
            "task": "classification",
            "targets": {"no diabetic retinopathy": 0, "mild diabetic retinopathy": 1,
                        "moderate diabetic retinopathy": 2, "severe diabetic retinopathy": 3,
                        "proliferative diabetic retinopathy": 4}}
    elif experiment == "02_MESSIDOR":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "02_MESSIDOR.csv",
                   "task": "classification",
                   "targets": {"no diabetic retinopathy": 0, "mild diabetic retinopathy": 1,
                               "moderate diabetic retinopathy": 2, "severe diabetic retinopathy": 3,
                               "proliferative diabetic retinopathy": 4}}
    elif experiment == "29_AIROGS":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "29_AIROGS.csv",
                   "task": "classification",
                   "targets": {"no glaucoma": 0, "glaucoma": 1}}
    elif experiment == "31_JICHI":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "31_JICHI.csv",
                   "task": "classification",
                   "targets": {'no diabetic retinopathy': 1, 'microaneurysm': 2, 'retinal hemorrhage': 3,
                               'hard exudate': 4, 'retinal edema': 5, 'more than three small soft exudates': 6,
                               'neovascularization': 7, 'preretinal haemorrhage': 8, 'fibrovascular proliferativemembrane': 9,
                               'tractionalretinaldetachment': 10, 'soft exudate': 11, 'varicose veins': 12,
                               'intraretinal microvascular abnormality': 13, 'non-perfusion area over one disc area': 14}}
    elif experiment == "25_REFUGE":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "25_REFUGE.csv",
                   "task": "classification",
                   "targets": {"no glaucoma": 0, "glaucoma": 1}}
    elif experiment == "13_FIVES":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "13_FIVES.csv",
                   "task": "classification",
                   "targets": {"normal": 0, "age related macular degeneration": 1, "diabetic retinopathy": 2,
                               "glaucoma": 3}}
    elif experiment == "08_ODIR200x3":
        setting = {"dataframe": PATH_DATAFRAME_TRANSFERABILITY_CLASSIFICATION + "08_ODIR200x3.csv",
                   "task": "classification",
                   "targets": {"normal": 0, "pathologic myopia": 1, "cataract": 2}}
    else:
        setting = None
        print("Experiment not prepared...")

    return setting