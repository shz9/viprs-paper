#!/bin/bash

sbatch -J "ukbb_50k_windowed/VIPRS" multi_pop_analysis/score/score_job.sh "ukbb_50k_windowed/VIPRS"
sbatch -J "ukbb_50k_windowed/VIPRS-GSv_p" multi_pop_analysis/score/score_job.sh "ukbb_50k_windowed/VIPRS-GSv_p"

sbatch -J "external/SBayesR" multi_pop_analysis/score/score_job.sh "external/SBayesR"
sbatch -J "external/Lassosum" multi_pop_analysis/score/score_job.sh "external/Lassosum"
sbatch -J "external/LDPred2-grid" multi_pop_analysis/score/score_job.sh "external/LDPred2-grid"
sbatch -J "external/PRScs" multi_pop_analysis/score/score_job.sh "external/PRScs"
sbatch -J "external/PRSice2" multi_pop_analysis/score/score_job.sh "external/PRSice2"
