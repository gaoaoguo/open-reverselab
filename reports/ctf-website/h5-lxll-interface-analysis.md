# h5.lxll.com Interface Analysis

## Basic Info

- Target: `https://h5.lxll.com/#/`
- Resolved entry: `https://h5.lxll.com/#/pages/login/login`
- App: LiXiao LaiLa H5 / Vue + uni-app/Vite
- Frontend version: `5.0.104`; build time: `2026-06-09 07:35:38`
- Main API hosts: `api.lxll.com`, `apiv2.lxll.com`

## Request Wrappers

| Wrapper | Base | Method | Auth/common headers |
|---|---|---|---|
| legacy | `https://api.lxll.com/request/{Action}` | POST | `x-ua: ct=2&v=5.0.104`; after login: `x-token-c`, `x-user-id` |
| new | `https://apiv2.lxll.com/{path}` | GET/POST/PUT/DELETE | `x-ua: ct=2&v=5.0.104`; after login: `Authorization: Bearer <accessToken>` |

## Dynamically Confirmed Requests

| Method | URL | Status | Notes |
|---|---|---:|---|
| GET | `https://apiv2.lxll.com/customer/global/configuration` | 200 | Global config; returns latest client version |
| POST | `https://api.lxll.com/request/CheckUserExistByPhone` | 200 | Pre-login phone/role existence check |
| POST | `https://apiv2.lxll.com/customer/login` | 400 | Password login endpoint; synthetic negative test returned code `10002` |
| POST | `https://lixiao-app-log.cn-hangzhou.log.aliyuncs.com/.../track` | 200 | Frontend telemetry |
| POST | `https://r.clarity.ms/collect` | 204 | Microsoft Clarity telemetry |

## Login-related Static Endpoints

| Method | URL | Key | Source chunk |
|---|---|---|---|
| POST | `https://api.lxll.com/request/CustomerLoginByCandidate` | CustomerLoginByCandidate | `pages-login-login.BSdoMFWR.js` |
| POST | `https://apiv2.lxll.com/customer/sms/code` | customerSmsCode | `pages-login-phoneLogin.CZBL8_sQ.js` |
| POST | `https://apiv2.lxll.com/customer/register` | customerRegister | `pages-login-loginInformation.Doxoof3-.js` |
| GET | `https://apiv2.lxll.com/customer/reset-password/users` | customerResetPasswordUsers | `pages-login-forgotPassword.bPGVT613.js` |
| POST | `https://apiv2.lxll.com/customer/reset-password` | customerResetPassword | `pages-login-resetPassword.DLhUHUY0.js` |
| POST | `https://api.lxll.com/request/CustomerBindWeChat` | CustomerBindWeChat | `pages-login-wechatBinding.BDCU-Z3w.js` |
| POST | `https://api.lxll.com/request/CustomerResetPassword` | CustomerResetPassword | `pages-information-changePassword-changePassword.5tB6a314.js` |
| POST | `https://apiv2.lxll.com/customer/user/delete` | customerUserDelete | `pages-setting-setting.o11R1hGr.js` |

## Business Endpoint Samples

| Method | URL | Key | Source chunk |
|---|---|---|---|
| POST | `https://api.lxll.com/request/CustomerCreateUserNotificationReadRecord` | CustomerCreateUserNotificationReadRecord | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerListNotification` | CustomerListNotification | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerGetCourseOrderCount` | CustomerGetCourseOrderCount | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherCheckExistInProgressOrder` | CustomerTeacherCheckExistInProgressOrder | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerRetrieveStudentMetric` | CustomerRetrieveStudentMetric | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerRetrieveTeacherMetric` | CustomerRetrieveTeacherMetric | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerApplyResetWeakPhoneCode` | CustomerApplyResetWeakPhoneCode | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerVerifyResetWeakPhoneCode` | CustomerVerifyResetWeakPhoneCode | `pages-index-index.DWwvg7KU.js` |
| POST | `https://api.lxll.com/request/CustomerQueryCourseDetail` | CustomerQueryCourseDetail | `CourseCard.DdiWeXe3.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherApproveDeleteClassRecordRequest` | CustomerTeacherApproveDeleteClassRecordRequest | `CourseCard.DdiWeXe3.js` |
| GET | `https://apiv2.lxll.com/customer/training` | customerTraining | `CourseCard.DdiWeXe3.js` |
| POST | `https://apiv2.lxll.com/customer/training/start` | courseStart | `CourseCard.DdiWeXe3.js` |
| POST | `https://apiv2.lxll.com/customer/training/resume` | courseResume | `CourseCard.DdiWeXe3.js` |
| POST | `https://apiv2.lxll.com/customer/training/complete` | customerCourseComplete | `CourseCard.DdiWeXe3.js` |
| POST | `https://api.lxll.com/request/CommonAudioGenerator` | CommonAudioGenerator | `audioMngStore.WMwk6n25.js` |
| POST | `https://api.lxll.com/request/CheckUserExistByPhone` | CheckUserExistByPhone | `pages-login-passwordLogin.smpD9QfS.js` |
| POST | `https://apiv2.lxll.com/customer/anti-forget/start` | customerAntiForgetStart | `pages-antiForgettingList-antiForgettingList.BhoGBBAe.js` |
| POST | `https://api.lxll.com/request/CustomerStudentQueryQuotaOverview` | CustomerStudentQueryQuotaOverview | `pages-my-my.On9jnbx4.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherQueryCommissionOverview` | CustomerTeacherQueryCommissionOverview | `pages-my-my.On9jnbx4.js` |
| POST | `https://api.lxll.com/request/CustomerStudentQueryDetail` | CustomerStudentQueryDetail | `pages-information-myInformation-myInformation.DTJ4mFTV.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherQueryDetail` | CustomerTeacherQueryDetail | `pages-information-myInformation-myInformation.DTJ4mFTV.js` |
| POST | `https://api.lxll.com/request/CustomerStudentUpdateDetail` | CustomerStudentUpdateDetail | `pages-information-myInformation-myInformation.DTJ4mFTV.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherUpdateDetail` | CustomerTeacherUpdateDetail | `pages-information-myInformation-myInformation.DTJ4mFTV.js` |
| GET | `https://apiv2.lxll.com/customer/anti-forget/detail` | customerAntiForgetDetail | `pages-antiForgettingList-antiForgettingDetail.B0cM1UrW.js` |
| POST | `https://apiv2.lxll.com/customer/anti-forget/progress/submit` | customerAntiForgetProgressSubmit | `pages-antiForgettingList-antiForgettingDetail.B0cM1UrW.js` |
| POST | `https://apiv2.lxll.com/customer/anti-forget/complete` | customerAntiForgetComplete | `pages-antiForgettingList-antiForgettingDetail.B0cM1UrW.js` |
| POST | `https://apiv2.lxll.com/customer/anti-forget/shuffle` | customerAntiForgetShuffle | `pages-antiForgettingList-antiForgettingDetail.B0cM1UrW.js` |
| GET | `https://apiv2.lxll.com/customer/anti-forget/result` | customerAntiForgetResult | `pages-antiForgettingList-antiForgettingResult.DVIxgm1A.js` |
| POST | `https://api.lxll.com/request/CustomerRemoveWordFromFavorite` | CustomerRemoveWordFromFavorite | `pages-favoriteWords-favoriteWords.Cjp1hDP9.js` |
| GET | `https://apiv2.lxll.com/customer/user/pagination/offset` | customerUserPaginationOffset | `WordList.BPl42Ql9.js` |
| POST | `https://apiv2.lxll.com/customer/user/pagination/offset` | customerUserPaginationOffset | `WordList.BPl42Ql9.js` |
| POST | `https://api.lxll.com/request/CustomerFavoriteWordListNewWords` | CustomerFavoriteWordListNewWords | `pages-favoriteWords-favoriteGrid.BTVsRZhu.js` |
| GET | `https://apiv2.lxll.com/customer/favorite/word/nine-grid` | customerFavoriteWordNineGrid | `pages-favoriteWords-favoriteGrid.BTVsRZhu.js` |
| POST | `https://api.lxll.com/request/CustomerQueryCourseOrderReportMetric` | CustomerQueryCourseOrderReportMetric | `pages-trainingRecords-personalClassRecord-personalClassRecord.CsRQAWvk.js` |
| POST | `https://api.lxll.com/request/CustomerTeacherSubmitFeedbackForCourseOrder` | CustomerTeacherSubmitFeedbackForCourseOrder | `pages-trainingRecords-personalClassRecord-personalClassRecord.CsRQAWvk.js` |

## Artifacts

- `exports/ctf-website/h5-lxll/analysis_result.json`
- `exports/ctf-website/h5-lxll/api_map.json`: frontend API constant map, 175 entries
- `exports/ctf-website/h5-lxll/all_chunks_api_uses.json`: parsed actual chunk call sites, 85 unique endpoints
- `exports/ctf-website/h5-lxll/static_endpoint_scan.json`
