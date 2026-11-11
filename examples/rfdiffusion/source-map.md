# 逐页主张与来源

原文定位、关键主张与证据边界。结构与测量图为原作者像素，新增图元原生可编辑。

## 01　RFdiffusion：从几何要求生成蛋白质

主张：RFdiffusion fine-tunes RoseTTAFold for conditional backbone generation; experiments test selected structures/functions.

原文：Watson et al., Nature 620, 1089–1100 (2023). DOI: 10.1038/s41586-023-06415-8

限定：Representative experimental example is not a universal success guarantee.

页源：page-68e141f44a0b43769a044d77d970f33a.page.yaml

原图资产：media/fig6-interface.png

## 02　设计任务先规定“做什么”，再寻找“怎么折叠”

主张：The task is inverse design from structural/functional specifications; backbone, sequence and motif are distinct objects.

原文：Watson et al., 2023, pp. 1089–1090; Fig. 4c.

限定：Conceptual relation, no synthetic protein coordinates.

页源：page-b07cf5f575824f74995f89168a145bf7.page.yaml

原图资产：media/fig4-p53.png

## 03　核心改造：让结构预测器学习“去噪”

主张：RF is fine-tuned with residue-frame noising; translations Gaussian, orientations rotational Brownian motion.

原文：Watson et al., 2023, pp. 1090–1091, Fig. 1a; SI §§1–2.

限定：Training relation simplified; not a complete architecture or equation reproduction.

页源：page-f4f405392ff8414a90915fae5e3fe5e8.page.yaml

原图资产：无；原生图元

## 04　采样逐步收紧可能解，最终形成蛋白质骨架

主张：Iterative denoising begins with random frames; prediction of clean structure is updated over steps.

原文：Watson et al., 2023, Fig. 1c, p. 1091; 300-residue unconditional trajectory.

限定：Diffusion step order is not physical folding dynamics.

页源：page-50f4fddffdeb49629133b2210c0867ab.page.yaml

原图资产：media/fig1-trajectory.png

## 05　高质量生成来自预训练、训练目标与轨迹一致性

主张：Ablating pretraining, fine-tuning, MSE, self-conditioning degrades 300-residue unconditional generation.

原文：Watson et al., 2023, Fig. 2e, p. 1092; Extended Data Fig. 1d–h.

限定：Ablation outcome is AF2 RMSD, not experimental folding success.

页源：page-7d298746551d42ba97a5c90c77d48b8b.page.yaml

原图资产：media/fig2-ablation.png

## 06　骨架生成之后，还要跨过三道验证关

主张：ProteinMPNN sequences and AF2 filters connect generated structures to experiments; validation is partially orthogonal.

原文：Watson et al., 2023, p. 1090; SI §§5.1–5.3, PDF pp. 80–82.

限定：Task-specific thresholds differ; AF2 validation is partially orthogonal.

页源：page-06f9c203db594e769fb61d2eb6152f94.page.yaml

原图资产：无；原生图元

## 07　无条件生成扩展了可设计骨架的规模

主张：Diverse monomers include successful 600-residue designs; whole distribution worsens at longer lengths; selected designs CD tested.

原文：Watson et al., 2023, Fig. 2a,c,f and pp. 1090–1093.

限定：600residue selected successful examples do not imply uniformly high success at600.

页源：page-1ae2919ed8dc446cb1dd39d479a9b761.page.yaml

原图资产：media/fig2-structures.png, media/fig2-rmsd-clean.png

## 08　条件改变几何边界，生成器补全剩余结构

主张：Conditions include symmetry, binding target, motif and symmetric motif, with task-specific fine-tuning where needed.

原文：Watson et al., 2023, Fig. 1b; pp. 1090, 1093, 1096.

限定：Common conditional framework includes task-specific fine-tuning.

页源：page-a6d2297917234fa4a7135b94ba792e75.page.yaml

原图资产：media/complete-08-in-sym.png, media/complete-08-out-sym.png, media/complete-08-in-target.png, media/clean-08-out-target.png, media/complete-08-in-motif.png, media/clean-08-out-motif.png

## 09　Motif 支架设计：更多任务能找到可行解

主张：RFdiffusion solves 23/25 problems vs RFjoint17 (SI Table10 union; main prose says19) and Hallucination15 across tested variants; not sample success rate.

原文：Watson et al., 2023, Fig. 4a; SI Tables 9–10, PDF pp. 84–87.

限定：Task coverage is distinct from per-design success; SI/main discrepancy disclosed.

页源：page-153a27376d504bc2b52c169aad4ac907.page.yaml

原图资产：media/final-09-motifs.png

## 10　固定 p53 螺旋后，新增支架可增强结合

主张：Two scaffolding designs bind MDM2 with KD0.7 and0.5nM versus cited native peptide600nM; no clinical efficacy claim.

原文：Watson et al., 2023, Fig. 4c,d, pp. 1095–1096; p53 peptide reference 42.

限定：Affinity result is in vitro binding, not clinical efficacy; no p53 aggregate success count used because main and caption denominators/definitions differ.

页源：page-a93c7822a4654fe29d4392691fdadb94.page.yaml

原图资产：media/fig4-p53.png, media/fig4-bli.png

## 11　对称性把单链生成扩展到更大的组装体

主张：Symmetric design yields experimentally consistent oligomers; 87/608 within95%SEC calibration CI, microscopy subset.

原文：Watson et al., 2023, Fig. 3b,c and p. 1093; SEC sample counts in main text.

限定：SEC criterion at95%calibration interval, microscopy subset only; not87 atomic structures.

页源：page-722cc38755c5415aa55a175baa0b4fa9.page.yaml

原图资产：media/final-11-assembly-c3-design.png, media/final-11-assembly-c3-af2.png, media/final-11-assembly-c3-em.png, media/final-11-assembly-c3-recon.png, media/final-11-assembly-c3-overlay.png, media/final-11-assembly-c6-design.png, media/final-11-assembly-c6-af2.png, media/final-11-assembly-c6-em.png, media/final-11-assembly-c6-recon.png, media/final-11-assembly-c6-overlay.png, media/final-11-assembly-d4-design.png, media/final-11-assembly-d4-af2.png, media/final-11-assembly-d4-em.png, media/final-11-assembly-d4-recon.png, media/final-11-assembly-d4-overlay.png

## 12　对称 motif 的功能来自指定残基，而非外形相似

主张：18/36 tested Ni binders bind; H52A weakens/abolishes binding in17/17 expressed mutants, one nonexpressed.

原文：Watson et al., 2023, Fig. 5b,c; p. 1096; Extended Data Fig. 7.

限定：18of36tested bind Ni;17of17expressed mutants lose/reduce binding, one unexpressed. Distinguish ITC and nsEM.

页源：page-706169e57e4645519ad2dd462d276a9a.page.yaml

原图资产：media/complete-12-nickel-generation.png, media/fig5-nickel-validation.png

## 13　从目标表面的热点出发，直接生成结合骨架

主张：Complex-finetuned model conditions on target interface hotspots; designs filtered then95 per target selected.

原文：Watson et al., 2023, Fig. 6a; p. 1096; SI §5 binder settings.

限定：95designs per target are selected after computational filtering.

页源：page-aa1ef8a1fe284e9a8983744eee455e24.page.yaml

原图资产：media/fig6-condition.png

## 14　五个靶点都有命中，但提升属于完整设计流程

主张：Overall19% BLI hits among selected panel; comparison combines RFdiffusion and AF2 filtering, assays differ.

原文：Watson et al., 2023, Fig. 6b and pp. 1097–1098; BLI versus historical YSD comparison.

限定：Historical YSD and current BLI differ; model and filter contributions are author attribution, not controlled causal isolation.

页源：page-8c6706e8d84646a191c89ca94208b33c.page.yaml

原图资产：media/fig6-rates.png

## 15　HA 结合蛋白的实验结构检验了原子级设计精度

主张：HA20KD28nM; cryoEM2.9Å; design-vs-complexRMSD0.63Å, binder alone0.60Å; single selected example.

原文：Watson et al., 2023, Fig. 6d–h, pp. 1098–1099; HA_20 / Iowa43 HA.

限定：2.9Å is map resolution;0.63Å is deviation; HA20 is one selected design.

页源：page-51bb46696333478194b6a4e0e07076e9.page.yaml

原图资产：media/fig6-cryo-clean.png, media/fig6-interface.png, media/final-15-binder.png

## 16　同一框架的“通用性”，由不同层次的证据支撑

主张：Evidence varies by task from computational geometry to functional and structural experiments.

原文：Watson et al., 2023, Figs. 2–6; SI §§5.1–5.3.

限定：Evidence maturity varies across tasks.

页源：page-48239ec072c2445fb644dbfe0a295cf5.page.yaml

原图资产：无；原生图元

## 17　催化位点能被固定，不等于新酶功能已实现

主张：Enzyme scaffolding requires fine-tuning; low in silico success; explicit ligand modeling absent and no catalytic activity result.

原文：Watson et al., 2023, Fig. 4f,g, p. 1096; Extended Data Fig. 6.

限定：No catalytic activity data; ligands not explicit in this publication version.

页源：page-df66e4f567124c75be148c0e8dd090e7.page.yaml

原图资产：media/fig4-enzyme.png, media/fig4-enzyme-rates-complete.png

## 18　RFdiffusion 提供的是可控的结构生成起点

主张：Presenter synthesis: reusable structural prior, geometric conditions, full validation stack; scope targeted cases.

原文：Watson et al., 2023, Discussion, p. 1099; synthesis by presenter.

限定：Presenter synthesis scoped to2023paper; no claims about later versions.

页源：page-53bad256de87492c9e262424513c96d7.page.yaml

原图资产：无；原生图元

## 19　备份｜逐任务成功率显示优势与失败并存

主张：All25 exact rows; shown max of tested variants separately for each method (not average or single configuration).

原文：Watson et al., 2023, SI Table 10 (PDF p. 87; printed p. 86); native redraw.

限定：Max across variants is summary, not one simultaneously achieved setting.

页源：page-ccc840bb3dc24f0db04e4ff2e7d2c5ca.page.yaml

原图资产：无；原生图元

## 20　备份｜评价器的设置随设计任务变化

主张：AF2 setup varies: single sequence; initial guess for oligomer/binder; targets templated; not fully independent.

原文：Watson et al., 2023, SI §§5.1–5.3, PDF pp. 80–82.

限定：Different AF2 input modes and confidence thresholds; no blanket independence claim.

页源：page-fd299ca7bbb347d9b774346710c318bb.page.yaml

原图资产：无；原生图元
