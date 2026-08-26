import React, { useState } from "react";
import { Language, ApplicantData } from "../types";
import { getT } from "../i18n";
import { CreditCard, Calendar, Receipt, DollarSign, Calculator, RotateCcw, AlertCircle } from "lucide-react";

interface AssessmentFormProps {
  currentLang: Language;
  applicant: ApplicantData;
  isLoading: boolean;
  onSubmit: (data: ApplicantData) => void;
  onReset: () => void;
}

export const AssessmentForm: React.FC<AssessmentFormProps> = ({
  currentLang,
  applicant,
  isLoading,
  onSubmit,
  onReset,
}) => {
  const t = getT(currentLang);
  const [formData, setFormData] = useState<ApplicantData>({ ...applicant });

  // Update field
  const handleChange = (field: keyof ApplicantData, value: number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const repaymentOptions = [
    { value: -2, label: t("opt_pay_neg2") },
    { value: -1, label: t("opt_pay_neg1") },
    { value: 0, label: t("opt_pay_0") },
    { value: 1, label: t("opt_pay_1") },
    { value: 2, label: t("opt_pay_2") },
    { value: 3, label: t("opt_pay_3") },
    { value: 4, label: t("opt_pay_4") },
    { value: 5, label: t("opt_pay_5") },
    { value: 6, label: t("opt_pay_6") },
    { value: 7, label: t("opt_pay_7") },
    { value: 8, label: t("opt_pay_8") },
  ];

  return (
    <div className="max-w-5xl w-full max-w-full mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs w-full max-w-full">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 gap-3 w-full max-w-full">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{t("form_title")}</h2>
            <p className="text-xs text-slate-500 mt-1 break-words">{t("form_desc")}</p>
          </div>
          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center justify-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3.5 py-2 sm:py-1.5 rounded-lg transition min-h-[38px] sm:min-h-[32px] self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t("btn_clear")}</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-5 sm:mt-6 space-y-6 sm:space-y-8 w-full max-w-full">
          {/* Section 1: Demographics & Credit Line */}
          <div className="space-y-3 sm:space-y-4 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
              <CreditCard className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">1. {t("form_sec_credit_profile")}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 w-full max-w-full">
              {/* Credit Limit */}
              <div className="sm:col-span-2 lg:col-span-2 min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {t("lbl_limit_bal")}
                </label>
                <div className="relative w-full max-w-full">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-xs text-slate-400 font-mono pointer-events-none">
                    NT$
                  </span>
                  <input
                    id="input-limit-bal"
                    type="number"
                    min="10000"
                    max="1000000"
                    step="5000"
                    value={formData.LIMIT_BAL}
                    onChange={(e) => handleChange("LIMIT_BAL", Number(e.target.value))}
                    className="w-full max-w-full min-w-0 pl-10 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 min-h-[42px] sm:min-h-[38px] box-border"
                    required
                  />
                </div>
              </div>

              {/* Gender */}
              <div className="min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {t("lbl_sex")}
                </label>
                <select
                  id="select-sex"
                  value={formData.SEX}
                  onChange={(e) => handleChange("SEX", Number(e.target.value))}
                  className="w-full max-w-full min-w-0 py-2 px-3 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 min-h-[42px] sm:min-h-[38px] box-border"
                >
                  <option value={1}>{t("lbl_sex_male")}</option>
                  <option value={2}>{t("lbl_sex_female")}</option>
                </select>
              </div>

              {/* Education */}
              <div className="min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {t("lbl_education")}
                </label>
                <select
                  id="select-education"
                  value={formData.EDUCATION}
                  onChange={(e) => handleChange("EDUCATION", Number(e.target.value))}
                  className="w-full max-w-full min-w-0 py-2 px-3 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 min-h-[42px] sm:min-h-[38px] box-border"
                >
                  <option value={1}>{t("lbl_edu_grad")}</option>
                  <option value={2}>{t("lbl_edu_uni")}</option>
                  <option value={3}>{t("lbl_edu_high")}</option>
                  <option value={4}>{t("lbl_edu_other")}</option>
                </select>
              </div>

              {/* Age */}
              <div className="min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  {t("lbl_age")}
                </label>
                <input
                  id="input-age"
                  type="number"
                  min="21"
                  max="79"
                  value={formData.AGE}
                  onChange={(e) => handleChange("AGE", Number(e.target.value))}
                  className="w-full max-w-full min-w-0 py-2 px-3 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 min-h-[42px] sm:min-h-[38px] box-border"
                  required
                />
              </div>
            </div>
          </div>

          {/* Section 2: Repayment Timeliness History */}
          <div className="space-y-3 sm:space-y-4 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
              <Calendar className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">2. {t("form_sec_repayment")}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5 sm:gap-3 w-full max-w-full">
              {[
                { key: "PAY_0", label: t("lbl_pay_0") },
                { key: "PAY_2", label: t("lbl_pay_2") },
                { key: "PAY_3", label: t("lbl_pay_3") },
                { key: "PAY_4", label: t("lbl_pay_4") },
                { key: "PAY_5", label: t("lbl_pay_5") },
                { key: "PAY_6", label: t("lbl_pay_6") },
              ].map((item) => (
                <div key={item.key} className="min-w-0 w-full max-w-full">
                  <label className="block text-[11px] sm:text-xs font-semibold text-slate-700 mb-1 truncate" title={item.label}>
                    {item.label}
                  </label>
                  <select
                    id={`select-${item.key.toLowerCase()}`}
                    value={formData[item.key as keyof ApplicantData]}
                    onChange={(e) => handleChange(item.key as keyof ApplicantData, Number(e.target.value))}
                    className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-2.5 sm:px-2 text-xs border border-slate-300 rounded-md focus:ring-2 focus:ring-sky-500 focus:border-sky-500 min-h-[38px] sm:min-h-[34px] box-border"
                  >
                    {repaymentOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Section 3: Statement Billed Amounts */}
          <div className="space-y-3 sm:space-y-4 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
              <Receipt className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">3. {t("form_sec_bills")}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5 sm:gap-3 w-full max-w-full">
              {[
                { key: "BILL_AMT1", label: t("lbl_bill_amt1") },
                { key: "BILL_AMT2", label: t("lbl_bill_amt2") },
                { key: "BILL_AMT3", label: t("lbl_bill_amt3") },
                { key: "BILL_AMT4", label: t("lbl_bill_amt4") },
                { key: "BILL_AMT5", label: t("lbl_bill_amt5") },
                { key: "BILL_AMT6", label: t("lbl_bill_amt6") },
              ].map((item) => (
                <div key={item.key} className="min-w-0 w-full max-w-full">
                  <label className="block text-[11px] sm:text-xs font-semibold text-slate-700 mb-1 truncate" title={item.label}>
                    {item.label}
                  </label>
                  <input
                    id={`input-${item.key.toLowerCase()}`}
                    type="number"
                    step="500"
                    value={formData[item.key as keyof ApplicantData]}
                    onChange={(e) => handleChange(item.key as keyof ApplicantData, Number(e.target.value))}
                    className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-2.5 sm:px-2 text-xs border border-slate-300 rounded-md focus:ring-2 focus:ring-sky-500 focus:border-sky-500 font-mono min-h-[38px] sm:min-h-[34px] box-border"
                    required
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Section 4: Paid Amounts */}
          <div className="space-y-3 sm:space-y-4 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
              <DollarSign className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">4. {t("form_sec_payments")}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5 sm:gap-3 w-full max-w-full">
              {[
                { key: "PAY_AMT1", label: t("lbl_pay_amt1") },
                { key: "PAY_AMT2", label: t("lbl_pay_amt2") },
                { key: "PAY_AMT3", label: t("lbl_pay_amt3") },
                { key: "PAY_AMT4", label: t("lbl_pay_amt4") },
                { key: "PAY_AMT5", label: t("lbl_pay_amt5") },
                { key: "PAY_AMT6", label: t("lbl_pay_amt6") },
              ].map((item) => (
                <div key={item.key} className="min-w-0 w-full max-w-full">
                  <label className="block text-[11px] sm:text-xs font-semibold text-slate-700 mb-1 truncate" title={item.label}>
                    {item.label}
                  </label>
                  <input
                    id={`input-${item.key.toLowerCase()}`}
                    type="number"
                    min="0"
                    step="500"
                    value={formData[item.key as keyof ApplicantData]}
                    onChange={(e) => handleChange(item.key as keyof ApplicantData, Number(e.target.value))}
                    className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-2.5 sm:px-2 text-xs border border-slate-300 rounded-md focus:ring-2 focus:ring-sky-500 focus:border-sky-500 font-mono min-h-[38px] sm:min-h-[34px] box-border"
                    required
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-end w-full max-w-full">
            <button
              id="btn-calculate-risk"
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center space-x-2 bg-sky-600 hover:bg-sky-700 disabled:bg-sky-400 text-white font-bold text-sm px-6 py-3 sm:py-2.5 rounded-lg shadow-xs transition min-h-[44px] w-full sm:w-auto"
            >
              <Calculator className="w-4 h-4" />
              <span>{isLoading ? t("msg_calculating") : t("btn_run_assessment")}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Disclaimers Banner */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 w-full max-w-full break-words leading-relaxed">
        <p><strong>🔒 Zero Identity Data:</strong> {t("disclaimer_privacy")}</p>
      </div>
    </div>
  );
};
