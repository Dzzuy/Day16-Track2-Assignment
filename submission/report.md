# Lab 16 CPU benchmark report

1. AWS us-east-1, `c7i-flex.large` (2 vCPU, 4 GiB), Ubuntu 22.04; source commit `55539f67d7c78b43afe334a2ec3271c4bfdbbe2d`. AWS rejected the starter `t3.medium` as ineligible for this account's Free Tier plan.
2. Kaggle Credit Card Fraud Detection: 284,807 rows, 492 frauds, no missing values. Stratified 60/20/20 train/validation/test split with seed 16 produced 170,883 / 56,962 / 56,962 rows.
3. In the VM run captured at 17:15 UTC, data load took 0.9943 seconds. LightGBM training took 2.2961 seconds, with early stopping at iteration 68; these times exclude VM setup and dataset download.
4. On the untouched test set: AUC-ROC 0.976848, Accuracy 0.999508, F1 0.847826, Precision 0.906977, Recall 0.795918. AUC uses predicted probabilities; the other scores use a 0.5 threshold.
5. Median `predict_proba` latency for one row was 0.5393 ms over 50 calls after warm-up. Median throughput for a batch of 1,000 rows was 530,262 rows/second over 10 calls; inference timing excludes loading and training.
6. In the post-benchmark screenshot from the first deployment at 15:50 UTC, CPU was 100% idle and memory use was 238 MiB of 3.7 GiB; interface `enp39s0` showed 279,673,075 received bytes and 1,002,302 transmitted bytes. These are post-run observations, and the network counters are cumulative rather than a transfer rate.
7. AWS Cost Management showed its first-visit message on 2026-10-03, saying cost and usage data may take 24 hours to prepare. No billed amount was available at capture time; evidence is in `screenshot/`.
8. `screenshot/cp3-benchmark-vm-run.png` shows the actual VM command and complete output for the JSON in this submission. The matching result was copied to the laptop before cleanup. Terraform destroyed all 27 resources in both deployments; the second cleanup finished by 2026-10-03 17:27 UTC and its state list is empty. See `cleanup.txt`.
