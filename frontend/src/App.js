// import { BrowserRouter, Route, Routes } from "react-router-dom";
// import HomePageOne from "./pages/HomePageOne";
// import HomePageTwo from "./pages/HomePageTwo";
// import HomePageThree from "./pages/HomePageThree";
// import HomePageFour from "./pages/HomePageFour";
// import HomePageFive from "./pages/HomePageFive";
// import HomePageSix from "./pages/HomePageSix";
// import HomePageSeven from "./pages/HomePageSeven";
// import EmailPage from "./pages/EmailPage";
// import AddUserPage from "./pages/AddUserPage";
// import AlertPage from "./pages/AlertPage";
// import AssignRolePage from "./pages/AssignRolePage";
// import AvatarPage from "./pages/AvatarPage";
// import BadgesPage from "./pages/BadgesPage";
// import ButtonPage from "./pages/ButtonPage";
// import CalendarMainPage from "./pages/CalendarMainPage";
// import CardPage from "./pages/CardPage";
// import CarouselPage from "./pages/CarouselPage";
// import ChatEmptyPage from "./pages/ChatEmptyPage";
// import ChatMessagePage from "./pages/ChatMessagePage";
// import ChatProfilePage from "./pages/ChatProfilePage";
// import CodeGeneratorNewPage from "./pages/CodeGeneratorNewPage";
// import CodeGeneratorPage from "./pages/CodeGeneratorPage";
// import ColorsPage from "./pages/ColorsPage";
// import ColumnChartPage from "./pages/ColumnChartPage";
// import CompanyPage from "./pages/CompanyPage";
// import CurrenciesPage from "./pages/CurrenciesPage";
// import DropdownPage from "./pages/DropdownPage";
// import ErrorPage from "./pages/ErrorPage";
// import FaqPage from "./pages/FaqPage";
// import ForgotPasswordPage from "./pages/ForgotPasswordPage";
// import FormLayoutPage from "./pages/FormLayoutPage";
// import FormValidationPage from "./pages/FormValidationPage";
// import FormPage from "./pages/FormPage";
// import GalleryPage from "./pages/GalleryPage";
// import ImageGeneratorPage from "./pages/ImageGeneratorPage";
// import ImageUploadPage from "./pages/ImageUploadPage";
// import InvoiceAddPage from "./pages/InvoiceAddPage";
// import InvoiceEditPage from "./pages/InvoiceEditPage";
// import InvoiceListPage from "./pages/InvoiceListPage";
// import InvoicePreviewPage from "./pages/InvoicePreviewPage";
// import KanbanPage from "./pages/KanbanPage";
// import LanguagePage from "./pages/LanguagePage";
// import LineChartPage from "./pages/LineChartPage";
// import ListPage from "./pages/ListPage";
// import MarketplaceDetailsPage from "./pages/MarketplaceDetailsPage";
// import MarketplacePage from "./pages/MarketplacePage";
// import NotificationAlertPage from "./pages/NotificationAlertPage";
// import NotificationPage from "./pages/NotificationPage";
// import PaginationPage from "./pages/PaginationPage";
// import PaymentGatewayPage from "./pages/PaymentGatewayPage";
// import PieChartPage from "./pages/PieChartPage";
// import PortfolioPage from "./pages/PortfolioPage";
// import PricingPage from "./pages/PricingPage";
// import ProgressPage from "./pages/ProgressPage";
// import RadioPage from "./pages/RadioPage";
// import RoleAccessPage from "./pages/RoleAccessPage";
// import SignInPage from "./pages/SignInPage";
// import SignUpPage from "./pages/SignUpPage";
// import StarRatingPage from "./pages/StarRatingPage";
// import StarredPage from "./pages/StarredPage";
// import SwitchPage from "./pages/SwitchPage";
// import TableBasicPage from "./pages/TableBasicPage";
// import TableDataPage from "./pages/TableDataPage";
// import TabsPage from "./pages/TabsPage";
// import TagsPage from "./pages/TagsPage";
// import TermsConditionPage from "./pages/TermsConditionPage";
// import TextGeneratorPage from "./pages/TextGeneratorPage";
// import ThemePage from "./pages/ThemePage";
// import TooltipPage from "./pages/TooltipPage";
// import TypographyPage from "./pages/TypographyPage";
// import UsersGridPage from "./pages/UsersGridPage";
// import UsersListPage from "./pages/UsersListPage";
// import ViewDetailsPage from "./pages/ViewDetailsPage";
// import VideoGeneratorPage from "./pages/VideoGeneratorPage";
// import VideosPage from "./pages/VideosPage";
// import ViewProfilePage from "./pages/ViewProfilePage";
// import VoiceGeneratorPage from "./pages/VoiceGeneratorPage";
// import WalletPage from "./pages/WalletPage";
// import WidgetsPage from "./pages/WidgetsPage";
// import WizardPage from "./pages/WizardPage";
// import RouteScrollToTop from "./helper/RouteScrollToTop";
// import TextGeneratorNewPage from "./pages/TextGeneratorNewPage";
// import HomePageEight from "./pages/HomePageEight";
// import HomePageNine from "./pages/HomePageNine";
// import HomePageTen from "./pages/HomePageTen";
// import HomePageEleven from "./pages/HomePageEleven";
// import GalleryGridPage from "./pages/GalleryGridPage";
// import GalleryMasonryPage from "./pages/GalleryMasonryPage";
// import GalleryHoverPage from "./pages/GalleryHoverPage";
// import BlogPage from "./pages/BlogPage";
// import BlogDetailsPage from "./pages/BlogDetailsPage";
// import AddBlogPage from "./pages/AddBlogPage";
// import TestimonialsPage from "./pages/TestimonialsPage";
// import ComingSoonPage from "./pages/ComingSoonPage";
// import AccessDeniedPage from "./pages/AccessDeniedPage";
// import MaintenancePage from "./pages/MaintenancePage";
// import BlankPagePage from "./pages/BlankPagePage";


// // master 
//  import DepartmentList from "./pages/masters/department/DepartmentList";
// import LeadsList from "./pages/leads/LeadsList";
// // import DepartmentList from "./pages/DepartmentList";

// function App() {
//   return (
//     <BrowserRouter>
//       <RouteScrollToTop />
//       <Routes>
//         <Route exact path='/' element={<HomePageOne />} />
//         <Route exact path='/index-2' element={<HomePageTwo />} />
//         <Route exact path='/index-3' element={<HomePageThree />} />
//         <Route exact path='/index-4' element={<HomePageFour />} />
//         <Route exact path='/index-5' element={<HomePageFive />} />
//         <Route exact path='/index-6' element={<HomePageSix />} />
//         <Route exact path='/index-7' element={<HomePageSeven />} />
//         <Route exact path='/index-8' element={<HomePageEight />} />
//         <Route exact path='/index-9' element={<HomePageNine />} />
//         <Route exact path='/index-10' element={<HomePageTen />} />
//         <Route exact path='/index-11' element={<HomePageEleven />} />

//         {/* SL */}
//         <Route exact path='/add-user' element={<AddUserPage />} />
//         <Route exact path='/alert' element={<AlertPage />} />
//         <Route exact path='/assign-role' element={<AssignRolePage />} />
//         <Route exact path='/avatar' element={<AvatarPage />} />
//         <Route exact path='/badges' element={<BadgesPage />} />
//         <Route exact path='/button' element={<ButtonPage />} />
//         <Route exact path='/calendar-main' element={<CalendarMainPage />} />
//         <Route exact path='/calendar' element={<CalendarMainPage />} />
//         <Route exact path='/card' element={<CardPage />} />
//         <Route exact path='/carousel' element={<CarouselPage />} />
//         <Route exact path='/chat-empty' element={<ChatEmptyPage />} />
//         <Route exact path='/chat-message' element={<ChatMessagePage />} />
//         <Route exact path='/chat-profile' element={<ChatProfilePage />} />
//         <Route exact path='/code-generator' element={<CodeGeneratorPage />} />
//         <Route
//           exact
//           path='/code-generator-new'
//           element={<CodeGeneratorNewPage />}
//         />
//         <Route exact path='/colors' element={<ColorsPage />} />
//         <Route exact path='/column-chart' element={<ColumnChartPage />} />
//         <Route exact path='/company' element={<CompanyPage />} />
//         <Route exact path='/currencies' element={<CurrenciesPage />} />
//         <Route exact path='/dropdown' element={<DropdownPage />} />
//         <Route exact path='/email' element={<EmailPage />} />
//         <Route exact path='/faq' element={<FaqPage />} />
//         <Route exact path='/forgot-password' element={<ForgotPasswordPage />} />
//         <Route exact path='/form-layout' element={<FormLayoutPage />} />
//         <Route exact path='/form-validation' element={<FormValidationPage />} />
//         <Route exact path='/form' element={<FormPage />} />

//         <Route exact path='/gallery' element={<GalleryPage />} />
//         <Route exact path='/gallery-grid' element={<GalleryGridPage />} />
//         <Route exact path='/gallery-masonry' element={<GalleryMasonryPage />} />
//         <Route exact path='/gallery-hover' element={<GalleryHoverPage />} />

//         <Route exact path='/blog' element={<BlogPage />} />
//         <Route exact path='/blog-details' element={<BlogDetailsPage />} />
//         <Route exact path='/add-blog' element={<AddBlogPage />} />

//         <Route exact path='/testimonials' element={<TestimonialsPage />} />
//         <Route exact path='/coming-soon' element={<ComingSoonPage />} />
//         <Route exact path='/access-denied' element={<AccessDeniedPage />} />
//         <Route exact path='/maintenance' element={<MaintenancePage />} />
//         <Route exact path='/blank-page' element={<BlankPagePage />} />

//         <Route exact path='/image-generator' element={<ImageGeneratorPage />} />
//         <Route exact path='/image-upload' element={<ImageUploadPage />} />
//         <Route exact path='/invoice-add' element={<InvoiceAddPage />} />
//         <Route exact path='/invoice-edit' element={<InvoiceEditPage />} />
//         <Route exact path='/invoice-list' element={<InvoiceListPage />} />
//         <Route exact path='/invoice-preview' element={<InvoicePreviewPage />} />
//         <Route exact path='/kanban' element={<KanbanPage />} />
//         <Route exact path='/language' element={<LanguagePage />} />
//         <Route exact path='/line-chart' element={<LineChartPage />} />
//         <Route exact path='/list' element={<ListPage />} />
//         <Route
//           exact
//           path='/marketplace-details'
//           element={<MarketplaceDetailsPage />}
//         />
//         <Route exact path='/marketplace' element={<MarketplacePage />} />
//         <Route
//           exact
//           path='/notification-alert'
//           element={<NotificationAlertPage />}
//         />
//         <Route exact path='/notification' element={<NotificationPage />} />
//         <Route exact path='/pagination' element={<PaginationPage />} />
//         <Route exact path='/payment-gateway' element={<PaymentGatewayPage />} />
//         <Route exact path='/pie-chart' element={<PieChartPage />} />
//         <Route exact path='/portfolio' element={<PortfolioPage />} />
//         <Route exact path='/pricing' element={<PricingPage />} />
//         <Route exact path='/progress' element={<ProgressPage />} />
//         <Route exact path='/radio' element={<RadioPage />} />
//         <Route exact path='/role-access' element={<RoleAccessPage />} />
//         <Route exact path='/sign-in' element={<SignInPage />} />
//         <Route exact path='/sign-up' element={<SignUpPage />} />
//         <Route exact path='/star-rating' element={<StarRatingPage />} />
//         <Route exact path='/starred' element={<StarredPage />} />
//         <Route exact path='/switch' element={<SwitchPage />} />
//         <Route exact path='/table-basic' element={<TableBasicPage />} />
//         <Route exact path='/table-data' element={<TableDataPage />} />
//         <Route exact path='/tabs' element={<TabsPage />} />
//         <Route exact path='/tags' element={<TagsPage />} />
//         <Route exact path='/terms-condition' element={<TermsConditionPage />} />
//         <Route
//           exact
//           path='/text-generator-new'
//           element={<TextGeneratorNewPage />}
//         />
//         <Route exact path='/text-generator' element={<TextGeneratorPage />} />
//         <Route exact path='/theme' element={<ThemePage />} />
//         <Route exact path='/tooltip' element={<TooltipPage />} />
//         <Route exact path='/typography' element={<TypographyPage />} />
//         <Route exact path='/users-grid' element={<UsersGridPage />} />
//         <Route exact path='/users-list' element={<UsersListPage />} />
//         <Route exact path='/view-details' element={<ViewDetailsPage />} />
//         <Route exact path='/video-generator' element={<VideoGeneratorPage />} />
//         <Route exact path='/videos' element={<VideosPage />} />
//         <Route exact path='/view-profile' element={<ViewProfilePage />} />
//         <Route exact path='/voice-generator' element={<VoiceGeneratorPage />} />
//         <Route exact path='/wallet' element={<WalletPage />} />
//         <Route exact path='/widgets' element={<WidgetsPage />} />
//         <Route exact path='/wizard' element={<WizardPage />} />



//         {/* master route */}


//           <Route exact path='/leads' element={<LeadsList />} />
//         <Route exact path='/department' element={<DepartmentList />} />
//         {/* <Route exact path='/department' element={<DepartmentList />} /> */}

//         <Route exact path='*' element={<ErrorPage />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import HomePageOne from "./pages/HomePageOne";
import HomePageTwo from "./pages/HomePageTwo";
import HomePageThree from "./pages/HomePageThree";
import HomePageFour from "./pages/HomePageFour";
import HomePageFive from "./pages/HomePageFive";
import HomePageSix from "./pages/HomePageSix";
import HomePageSeven from "./pages/HomePageSeven";
import EmailPage from "./pages/EmailPage";
import AddUserPage from "./pages/AddUserPage";
import AlertPage from "./pages/AlertPage";
import AssignRolePage from "./pages/AssignRolePage";
import AvatarPage from "./pages/AvatarPage";
import BadgesPage from "./pages/BadgesPage";
import ButtonPage from "./pages/ButtonPage";
import CalendarMainPage from "./pages/CalendarMainPage";
import CardPage from "./pages/CardPage";
import CarouselPage from "./pages/CarouselPage";
import ChatEmptyPage from "./pages/ChatEmptyPage";
import ChatMessagePage from "./pages/ChatMessagePage";
import ChatProfilePage from "./pages/ChatProfilePage";
import CodeGeneratorNewPage from "./pages/CodeGeneratorNewPage";
import CodeGeneratorPage from "./pages/CodeGeneratorPage";
import ColorsPage from "./pages/ColorsPage";
import ColumnChartPage from "./pages/ColumnChartPage";
import CompanyPage from "./pages/CompanyPage";
import CurrenciesPage from "./pages/CurrenciesPage";
import DropdownPage from "./pages/DropdownPage";
import ErrorPage from "./pages/ErrorPage";
import FaqPage from "./pages/FaqPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import FormLayoutPage from "./pages/FormLayoutPage";
import FormValidationPage from "./pages/FormValidationPage";
import FormPage from "./pages/FormPage";
import GalleryPage from "./pages/GalleryPage";
import ImageGeneratorPage from "./pages/ImageGeneratorPage";
import ImageUploadPage from "./pages/ImageUploadPage";
import InvoiceAddPage from "./pages/InvoiceAddPage";
import InvoiceEditPage from "./pages/InvoiceEditPage";
import InvoiceListPage from "./pages/InvoiceListPage";
import InvoicePreviewPage from "./pages/InvoicePreviewPage";
import KanbanPage from "./pages/KanbanPage";
import LanguagePage from "./pages/LanguagePage";
import LineChartPage from "./pages/LineChartPage";
import ListPage from "./pages/ListPage";
import MarketplaceDetailsPage from "./pages/MarketplaceDetailsPage";
import MarketplacePage from "./pages/MarketplacePage";
import NotificationAlertPage from "./pages/NotificationAlertPage";
import NotificationPage from "./pages/NotificationPage";
import PaginationPage from "./pages/PaginationPage";
import PaymentGatewayPage from "./pages/PaymentGatewayPage";
import PieChartPage from "./pages/PieChartPage";
import PortfolioPage from "./pages/PortfolioPage";
import PricingPage from "./pages/PricingPage";
import ProgressPage from "./pages/ProgressPage";
import RadioPage from "./pages/RadioPage";
import RoleAccessPage from "./pages/RoleAccessPage";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import StarRatingPage from "./pages/StarRatingPage";
import StarredPage from "./pages/StarredPage";
import SwitchPage from "./pages/SwitchPage";
import TableBasicPage from "./pages/TableBasicPage";
import TableDataPage from "./pages/TableDataPage";
import TabsPage from "./pages/TabsPage";
import TagsPage from "./pages/TagsPage";
import TermsConditionPage from "./pages/TermsConditionPage";
import TextGeneratorPage from "./pages/TextGeneratorPage";
import ThemePage from "./pages/ThemePage";
import TooltipPage from "./pages/TooltipPage";
import TypographyPage from "./pages/TypographyPage";
import UsersGridPage from "./pages/UsersGridPage";
import UsersListPage from "./pages/UsersListPage";
import ViewDetailsPage from "./pages/ViewDetailsPage";
import VideoGeneratorPage from "./pages/VideoGeneratorPage";
import VideosPage from "./pages/VideosPage";
import ViewProfilePage from "./pages/ViewProfilePage";
import VoiceGeneratorPage from "./pages/VoiceGeneratorPage";
import WalletPage from "./pages/WalletPage";
import WidgetsPage from "./pages/WidgetsPage";
import WizardPage from "./pages/WizardPage";
import RouteScrollToTop from "./helper/RouteScrollToTop";
import TextGeneratorNewPage from "./pages/TextGeneratorNewPage";
import HomePageEight from "./pages/HomePageEight";
import HomePageNine from "./pages/HomePageNine";
import HomePageTen from "./pages/HomePageTen";
import HomePageEleven from "./pages/HomePageEleven";
import GalleryGridPage from "./pages/GalleryGridPage";
import GalleryMasonryPage from "./pages/GalleryMasonryPage";
import GalleryHoverPage from "./pages/GalleryHoverPage";
import BlogPage from "./pages/BlogPage";
import BlogDetailsPage from "./pages/BlogDetailsPage";
import AddBlogPage from "./pages/AddBlogPage";
import TestimonialsPage from "./pages/TestimonialsPage";
import ComingSoonPage from "./pages/ComingSoonPage";
import AccessDeniedPage from "./pages/AccessDeniedPage";
import MaintenancePage from "./pages/MaintenancePage";
import BlankPagePage from "./pages/BlankPagePage";

// master 
import DepartmentList from "./pages/masters/department/DepartmentList";
import EmployeeTypeList from "./pages/masters/employeeType/EmployeeTypeList";
import CompanyList from "./pages/masters/company/CompanyList";
import StakeholderCategoriesList from "./pages/masters/stakeholderCategories/StakeholderCategoriesList";
import LeadSourceList from "./pages/masters/salesMasters/leadSource/LeadSourceList"
import PriorityTypeList from "./pages/masters/priorityType/PriorityTypeList";
import TagsTypeList from "./pages/masters/tagsType/TagsTypeList";
import ActivityTypeList from "./pages/masters/salesMasters/activityType/ActivityTypeList";
import LostReasonB2CList from "./pages/masters/salesMasters/lostReasonB2C/LostReasonB2CList";
import LostReasonB2BList from "./pages/masters/salesMasters/lostReasonB2B/LostReasonB2BList";
 import InterestLevelList from "./pages/masters/salesMasters/interestLevel/InterestLevelList";
import LeadsList from "./pages/leads/LeadsList";
import BankAccountTypeList from "./pages/masters/companyMaster/bankAccountType/BankAccountTypeList";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  // Check if user is authenticated
  const isAuthenticated = () => {
    try {
      const authUser = localStorage.getItem('authUser');
      if (!authUser) return false;

      const userData = JSON.parse(authUser);

      // Check if access token exists
      if (!userData.access) return false;

      // Optional: Decode JWT and check expiration
      const tokenPayload = JSON.parse(atob(userData.access.split('.')[1]));
      const isExpired = tokenPayload.exp * 1000 < Date.now();

      if (isExpired) {
        // Token expired, clear storage
        localStorage.removeItem('authUser');
        return false;
      }

      return true;
    } catch (error) {
      console.error('Authentication check failed:', error);
      return false;
    }
  };

  if (!isAuthenticated()) {
    // Redirect to sign-in page if not authenticated
    return <Navigate to="/sign-in" replace />;
  }

  return children;
};

// Public Route Component (redirect to home if already logged in)
const PublicRoute = ({ children }) => {
  const isAuthenticated = () => {
    try {
      const authUser = localStorage.getItem('authUser');
      if (!authUser) return false;

      const userData = JSON.parse(authUser);
      return userData.access !== null && userData.access !== undefined;
    } catch (error) {
      return false;
    }
  };

  if (isAuthenticated()) {
    // Redirect to home page if already authenticated
    return <Navigate to="/" replace />;
  }

  return children;
};
function App() {
  return (
    <BrowserRouter>
      <RouteScrollToTop />
      <Routes>
        {/* Public Routes - Accessible without login */}
        <Route path='/sign-in' element={
          <PublicRoute>
            <SignInPage />
          </PublicRoute>
        } />
        <Route path='/sign-up' element={
          <PublicRoute>
            <SignUpPage />
          </PublicRoute>
        } />
        <Route path='/forgot-password' element={<ForgotPasswordPage />} />
        <Route path='/terms-condition' element={<TermsConditionPage />} />
        <Route path='/coming-soon' element={<ComingSoonPage />} />
        <Route path='/access-denied' element={<AccessDeniedPage />} />
        <Route path='/maintenance' element={<MaintenancePage />} />

        {/* Protected Routes - Require authentication */}
        <Route path='/' element={
          <ProtectedRoute>
            <HomePageOne />
          </ProtectedRoute>
        } />
        <Route path='/index-2' element={
          <ProtectedRoute>
            <HomePageTwo />
          </ProtectedRoute>
        } />
        <Route path='/index-3' element={
          <ProtectedRoute>
            <HomePageThree />
          </ProtectedRoute>
        } />
        <Route path='/index-4' element={
          <ProtectedRoute>
            <HomePageFour />
          </ProtectedRoute>
        } />
        <Route path='/index-5' element={
          <ProtectedRoute>
            <HomePageFive />
          </ProtectedRoute>
        } />
        <Route path='/index-6' element={
          <ProtectedRoute>
            <HomePageSix />
          </ProtectedRoute>
        } />
        <Route path='/index-7' element={
          <ProtectedRoute>
            <HomePageSeven />
          </ProtectedRoute>
        } />
        <Route path='/index-8' element={
          <ProtectedRoute>
            <HomePageEight />
          </ProtectedRoute>
        } />
        <Route path='/index-9' element={
          <ProtectedRoute>
            <HomePageNine />
          </ProtectedRoute>
        } />
        <Route path='/index-10' element={
          <ProtectedRoute>
            <HomePageTen />
          </ProtectedRoute>
        } />
        <Route path='/index-11' element={
          <ProtectedRoute>
            <HomePageEleven />
          </ProtectedRoute>
        } />

        {/* All other protected routes */}
        <Route path='/add-user' element={<ProtectedRoute><AddUserPage /></ProtectedRoute>} />
        <Route path='/alert' element={<ProtectedRoute><AlertPage /></ProtectedRoute>} />
        <Route path='/assign-role' element={<ProtectedRoute><AssignRolePage /></ProtectedRoute>} />
        <Route path='/avatar' element={<ProtectedRoute><AvatarPage /></ProtectedRoute>} />
        <Route path='/badges' element={<ProtectedRoute><BadgesPage /></ProtectedRoute>} />
        <Route path='/button' element={<ProtectedRoute><ButtonPage /></ProtectedRoute>} />
        <Route path='/calendar-main' element={<ProtectedRoute><CalendarMainPage /></ProtectedRoute>} />
        <Route path='/calendar' element={<ProtectedRoute><CalendarMainPage /></ProtectedRoute>} />
        <Route path='/card' element={<ProtectedRoute><CardPage /></ProtectedRoute>} />
        <Route path='/carousel' element={<ProtectedRoute><CarouselPage /></ProtectedRoute>} />
        <Route path='/chat-empty' element={<ProtectedRoute><ChatEmptyPage /></ProtectedRoute>} />
        <Route path='/chat-message' element={<ProtectedRoute><ChatMessagePage /></ProtectedRoute>} />
        <Route path='/chat-profile' element={<ProtectedRoute><ChatProfilePage /></ProtectedRoute>} />
        <Route path='/code-generator' element={<ProtectedRoute><CodeGeneratorPage /></ProtectedRoute>} />
        <Route path='/code-generator-new' element={<ProtectedRoute><CodeGeneratorNewPage /></ProtectedRoute>} />
        <Route path='/colors' element={<ProtectedRoute><ColorsPage /></ProtectedRoute>} />
        <Route path='/column-chart' element={<ProtectedRoute><ColumnChartPage /></ProtectedRoute>} />
        <Route path='/company' element={<ProtectedRoute><CompanyPage /></ProtectedRoute>} />
        <Route path='/currencies' element={<ProtectedRoute><CurrenciesPage /></ProtectedRoute>} />
        <Route path='/dropdown' element={<ProtectedRoute><DropdownPage /></ProtectedRoute>} />
        <Route path='/email' element={<ProtectedRoute><EmailPage /></ProtectedRoute>} />
        <Route path='/faq' element={<ProtectedRoute><FaqPage /></ProtectedRoute>} />
        <Route path='/form-layout' element={<ProtectedRoute><FormLayoutPage /></ProtectedRoute>} />
        <Route path='/form-validation' element={<ProtectedRoute><FormValidationPage /></ProtectedRoute>} />
        <Route path='/form' element={<ProtectedRoute><FormPage /></ProtectedRoute>} />
        <Route path='/gallery' element={<ProtectedRoute><GalleryPage /></ProtectedRoute>} />
        <Route path='/gallery-grid' element={<ProtectedRoute><GalleryGridPage /></ProtectedRoute>} />
        <Route path='/gallery-masonry' element={<ProtectedRoute><GalleryMasonryPage /></ProtectedRoute>} />
        <Route path='/gallery-hover' element={<ProtectedRoute><GalleryHoverPage /></ProtectedRoute>} />
        <Route path='/blog' element={<ProtectedRoute><BlogPage /></ProtectedRoute>} />
        <Route path='/blog-details' element={<ProtectedRoute><BlogDetailsPage /></ProtectedRoute>} />
        <Route path='/add-blog' element={<ProtectedRoute><AddBlogPage /></ProtectedRoute>} />
        <Route path='/testimonials' element={<ProtectedRoute><TestimonialsPage /></ProtectedRoute>} />
        <Route path='/blank-page' element={<ProtectedRoute><BlankPagePage /></ProtectedRoute>} />
        <Route path='/image-generator' element={<ProtectedRoute><ImageGeneratorPage /></ProtectedRoute>} />
        <Route path='/image-upload' element={<ProtectedRoute><ImageUploadPage /></ProtectedRoute>} />
        <Route path='/invoice-add' element={<ProtectedRoute><InvoiceAddPage /></ProtectedRoute>} />
        <Route path='/invoice-edit' element={<ProtectedRoute><InvoiceEditPage /></ProtectedRoute>} />
        <Route path='/invoice-list' element={<ProtectedRoute><InvoiceListPage /></ProtectedRoute>} />
        <Route path='/invoice-preview' element={<ProtectedRoute><InvoicePreviewPage /></ProtectedRoute>} />
        <Route path='/kanban' element={<ProtectedRoute><KanbanPage /></ProtectedRoute>} />
        <Route path='/language' element={<ProtectedRoute><LanguagePage /></ProtectedRoute>} />
        <Route path='/line-chart' element={<ProtectedRoute><LineChartPage /></ProtectedRoute>} />
        <Route path='/list' element={<ProtectedRoute><ListPage /></ProtectedRoute>} />
        <Route path='/marketplace-details' element={<ProtectedRoute><MarketplaceDetailsPage /></ProtectedRoute>} />
        <Route path='/marketplace' element={<ProtectedRoute><MarketplacePage /></ProtectedRoute>} />
        <Route path='/notification-alert' element={<ProtectedRoute><NotificationAlertPage /></ProtectedRoute>} />
        <Route path='/notification' element={<ProtectedRoute><NotificationPage /></ProtectedRoute>} />
        <Route path='/pagination' element={<ProtectedRoute><PaginationPage /></ProtectedRoute>} />
        <Route path='/payment-gateway' element={<ProtectedRoute><PaymentGatewayPage /></ProtectedRoute>} />
        <Route path='/pie-chart' element={<ProtectedRoute><PieChartPage /></ProtectedRoute>} />
        <Route path='/portfolio' element={<ProtectedRoute><PortfolioPage /></ProtectedRoute>} />
        <Route path='/pricing' element={<ProtectedRoute><PricingPage /></ProtectedRoute>} />
        <Route path='/progress' element={<ProtectedRoute><ProgressPage /></ProtectedRoute>} />
        <Route path='/radio' element={<ProtectedRoute><RadioPage /></ProtectedRoute>} />
        <Route path='/role-access' element={<ProtectedRoute><RoleAccessPage /></ProtectedRoute>} />
        <Route path='/star-rating' element={<ProtectedRoute><StarRatingPage /></ProtectedRoute>} />
        <Route path='/starred' element={<ProtectedRoute><StarredPage /></ProtectedRoute>} />
        <Route path='/switch' element={<ProtectedRoute><SwitchPage /></ProtectedRoute>} />
        <Route path='/table-basic' element={<ProtectedRoute><TableBasicPage /></ProtectedRoute>} />
        <Route path='/table-data' element={<ProtectedRoute><TableDataPage /></ProtectedRoute>} />
        <Route path='/tabs' element={<ProtectedRoute><TabsPage /></ProtectedRoute>} />
        <Route path='/tags' element={<ProtectedRoute><TagsPage /></ProtectedRoute>} />
        <Route path='/text-generator-new' element={<ProtectedRoute><TextGeneratorNewPage /></ProtectedRoute>} />
        <Route path='/text-generator' element={<ProtectedRoute><TextGeneratorPage /></ProtectedRoute>} />
        <Route path='/theme' element={<ProtectedRoute><ThemePage /></ProtectedRoute>} />
        <Route path='/tooltip' element={<ProtectedRoute><TooltipPage /></ProtectedRoute>} />
        <Route path='/typography' element={<ProtectedRoute><TypographyPage /></ProtectedRoute>} />
        <Route path='/users-grid' element={<ProtectedRoute><UsersGridPage /></ProtectedRoute>} />
        <Route path='/users-list' element={<ProtectedRoute><UsersListPage /></ProtectedRoute>} />
        <Route path='/view-details' element={<ProtectedRoute><ViewDetailsPage /></ProtectedRoute>} />
        <Route path='/video-generator' element={<ProtectedRoute><VideoGeneratorPage /></ProtectedRoute>} />
        <Route path='/videos' element={<ProtectedRoute><VideosPage /></ProtectedRoute>} />
        <Route path='/view-profile' element={<ProtectedRoute><ViewProfilePage /></ProtectedRoute>} />
        <Route path='/voice-generator' element={<ProtectedRoute><VoiceGeneratorPage /></ProtectedRoute>} />
        <Route path='/wallet' element={<ProtectedRoute><WalletPage /></ProtectedRoute>} />
        <Route path='/widgets' element={<ProtectedRoute><WidgetsPage /></ProtectedRoute>} />
        <Route path='/wizard' element={<ProtectedRoute><WizardPage /></ProtectedRoute>} />

        {/* Master routes - Protected */}
        <Route path='/leads' element={<ProtectedRoute><LeadsList /></ProtectedRoute>} />
        <Route path='/department' element={<ProtectedRoute><DepartmentList /></ProtectedRoute>} />
        <Route path='/employeetype' element={<ProtectedRoute><EmployeeTypeList /></ProtectedRoute>} />
        <Route path='/companylist' element={<ProtectedRoute><CompanyList /></ProtectedRoute>} />
        <Route path='/stakeholder-list' element={<ProtectedRoute><StakeholderCategoriesList /></ProtectedRoute>} />
        <Route path='/lead-source' element={<ProtectedRoute><LeadSourceList /></ProtectedRoute>} />
        <Route path='/interest-level' element={<ProtectedRoute><InterestLevelList /></ProtectedRoute>} />
        <Route path='/priority-type' element={<ProtectedRoute><PriorityTypeList /></ProtectedRoute>} />
        <Route path='/tags-type' element={<ProtectedRoute><TagsTypeList /></ProtectedRoute>} />
        <Route path='/activity-type' element={<ProtectedRoute><ActivityTypeList /></ProtectedRoute>} />
        <Route path='/lost-reason-B2C' element={<ProtectedRoute><LostReasonB2CList /></ProtectedRoute>} />
        <Route path='/lost-reason-B2B' element={<ProtectedRoute><LostReasonB2BList /></ProtectedRoute>} />
        <Route path='/bank-ccount-type' element={<ProtectedRoute><BankAccountTypeList /></ProtectedRoute>} />
        {/* 404 Error Page */}
        <Route path='*' element={<ErrorPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;