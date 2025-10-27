// import { Icon } from "@iconify/react/dist/iconify.js";
// import React from "react";
// import { Link } from "react-router-dom";

// const SignInLayer = () => {
//   return (
//     <section className='auth bg-base d-flex flex-wrap'>
//       <div className='auth-left d-lg-block d-none'>
//         <div className='d-flex align-items-center flex-column h-100 justify-content-center'>
//           {/* <img src='assets/images/auth/auth-img.png' alt='' /> */}
//         </div>
//       </div>
//       <div className='auth-right py-32 px-24 d-flex flex-column justify-content-center'>
//         <div className='max-w-464-px mx-auto w-100'>
//           <div>
//             {/* <Link to='/' className='mb-40 max-w-290-px'>
//               <img src='assets/images/logo.png' alt='' />
//             </Link> */}
//             <h4 className='mb-12'>Sign In to your Account</h4>
//             <p className='mb-32 text-secondary-light text-lg'>
//               Welcome back! please enter your detail
//             </p>
//           </div>
//           <form action='#'>
//             <div className='icon-field mb-16'>
//               <span className='icon top-50 translate-middle-y'>
//                 <Icon icon='mage:email' />
//               </span>
//               <input
//                 type='email'
//                 className='form-control h-56-px bg-neutral-50 radius-12'
//                 placeholder='Email'
//               />
//             </div>
//             <div className='position-relative mb-20'>
//               <div className='icon-field'>
//                 <span className='icon top-50 translate-middle-y'>
//                   <Icon icon='solar:lock-password-outline' />
//                 </span>
//                 <input
//                   type='password'
//                   className='form-control h-56-px bg-neutral-50 radius-12'
//                   id='your-password'
//                   placeholder='Password'
//                 />
//               </div>
//               <span
//                 className='toggle-password ri-eye-line cursor-pointer position-absolute end-0 top-50 translate-middle-y me-16 text-secondary-light'
//                 data-toggle='#your-password'
//               />
//             </div>
//             <div className=''>
//               <div className='d-flex justify-content-between gap-2'>
//                 <div className='form-check style-check d-flex align-items-center'>
//                   <input
//                     className='form-check-input border border-neutral-300'
//                     type='checkbox'
//                     defaultValue=''
//                     id='remeber'
//                   />
//                   <label className='form-check-label' htmlFor='remeber'>
//                     Remember me{" "}
//                   </label>
//                 </div>
//                 <Link to='#' className='text-primary-600 fw-medium'>
//                   Forgot Password?
//                 </Link>
//               </div>
//             </div>
//             <button
//               type='submit'
//               className='btn btn-primary text-sm btn-sm px-12 py-16 w-100 radius-12 mt-32'
//             >
//               {" "}
//               Sign In
//             </button>
//             <div className='mt-32 center-border-horizontal text-center'>
//               <span className='bg-base z-1 px-4'>Or sign in with</span>
//             </div>
//             {/* <div className='mt-32 d-flex align-items-center gap-3'>
//               <button
//                 type='button'
//                 className='fw-semibold text-primary-light py-16 px-24 w-50 border radius-12 text-md d-flex align-items-center justify-content-center gap-12 line-height-1 bg-hover-primary-50'
//               >
//                 <Icon
//                   icon='ic:baseline-facebook'
//                   className='text-primary-600 text-xl line-height-1'
//                 />
//                 Google
//               </button>
//               <button
//                 type='button'
//                 className='fw-semibold text-primary-light py-16 px-24 w-50 border radius-12 text-md d-flex align-items-center justify-content-center gap-12 line-height-1 bg-hover-primary-50'
//               >
//                 <Icon
//                   icon='logos:google-icon'
//                   className='text-primary-600 text-xl line-height-1'
//                 />
//                 Google
//               </button>
//             </div> */}
//             <div className='mt-32 text-center text-sm'>
//               <p className='mb-0'>
//                 Don’t have an account?{" "}
//                 <Link to='/sign-up' className='text-primary-600 fw-semibold'>
//                   Sign Up
//                 </Link>
//               </p>
//             </div>
//           </form>
//         </div>
//       </div>
//     </section>
//   );
// };

// export default SignInLayer;

import { Icon } from "@iconify/react/dist/iconify.js";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useFormik } from "formik";
import * as Yup from "yup";
import { useDispatch, useSelector } from "react-redux";
import { loginUser } from "../../src/store/auth/login/actions";
import { toast } from "react-toastify";
const SignInLayer = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Get loading and error state from Redux
  // const { loading, error } = useSelector((state) => state.auth);

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Formik validation
  const validation = useFormik({
    enableReinitialize: true,
    initialValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .required("Email is required")
        .email("Please enter a valid email address"),
      password: Yup.string()
        .required("Password is required")
        .min(6, "Password must be at least 6 characters"),
    }),
    onSubmit: (values) => {
      // Dispatch Redux action
      const sendPayload = {
        email: values.email,
        password: values.password,

      }
      setLoading(true);
      dispatch(
        loginUser(sendPayload, navigate, (response, error) => {
          console.log("11111111111111111111:", response);
          if (response?.statusCode === 200) {
            setLoading(false);
            localStorage.setItem("authUser", JSON.stringify(response?.data));
            toast.success('Login successful');
            // Navigate to a path
            navigate('/')
          } else if (error) {

            toast.error(error?.message);
            setLoading(false);
            console.error("Login error:", error?.message);
          }
        })
      );
    },
  });

  return (
    <section className="auth bg-base d-flex flex-wrap">
      <div className="auth-left d-lg-block d-none">
        <div className="d-flex align-items-center flex-column h-100 justify-content-center">
          {/* <img src="assets/images/auth/auth-img.png" alt="Auth" /> */}
           <img src="assets/images/auth/logo-test1.png" alt="Auth" />
        </div>
      </div>
      <div className="auth-right py-32 px-24 d-flex flex-column justify-content-center">
        <div className="max-w-464-px mx-auto w-100">
          <div>
            <Link to="/" className="mb-40 max-w-290-px">
              {/* <img src="assets/images/logo.png" alt="Logo" /> */}
            </Link>
            <h4 className="mb-12">Sign In to your Account</h4>
            <p className="mb-32 text-secondary-light text-lg">
              Welcome back! please enter your detail
            </p>
          </div>

          {/* Show error from Redux if exists */}
          {error && (
            <div className="alert alert-danger mb-3" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={validation.handleSubmit}>
            {/* Email Field */}
            <div className="icon-field mb-16">
              <span className="icon top-50 translate-middle-y">
                <Icon icon="mage:email" />
              </span>
              <input
                type="email"
                name="email"
                className={`form-control h-56-px bg-neutral-50 radius-12 ${validation.touched.email && validation.errors.email
                  ? "is-invalid"
                  : ""
                  }`}
                placeholder="Email"
                onChange={validation.handleChange}
                onBlur={validation.handleBlur}
                value={validation.values.email}
                disabled={loading}
              />
              {validation.touched.email && validation.errors.email && (
                <div className="invalid-feedback d-block">
                  {validation.errors.email}
                </div>
              )}
            </div>

            {/* Password Field */}
            <div className="position-relative mb-20">
              <div className="icon-field">
                <span className="icon top-50 translate-middle-y">
                  <Icon icon="solar:lock-password-outline" />
                </span>
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  className={`form-control h-56-px bg-neutral-50 radius-12 ${validation.touched.password && validation.errors.password
                    ? "is-invalid"
                    : ""
                    }`}
                  placeholder="Password"
                  onChange={validation.handleChange}
                  onBlur={validation.handleBlur}
                  value={validation.values.password}
                  disabled={loading}
                />
                <span
                  className="toggle-password cursor-pointer position-absolute end-0 top-50 translate-middle-y me-16 text-secondary-light"
                  onClick={togglePasswordVisibility}
                >
                  <Icon
                    icon={showPassword ? "mdi:eye-off" : "mdi:eye"}
                    className="text-xl"
                  />
                </span>
              </div>
              {validation.touched.password && validation.errors.password && (
                <div className="text-danger text-sm mt-1">
                  {validation.errors.password}
                </div>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="d-flex justify-content-between gap-2">
              <div className="form-check style-check d-flex align-items-center">
                <input
                  className="form-check-input border border-neutral-300"
                  type="checkbox"
                  name="rememberMe"
                  id="rememberMe"
                  onChange={validation.handleChange}
                  checked={validation.values.rememberMe}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="rememberMe">
                  Remember me
                </label>
              </div>
              <Link to="/forgot-password" className="text-primary-600 fw-medium">
                Forgot Password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="btn btn-primary text-sm btn-sm px-12 py-16 w-100 radius-12 mt-32"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </button>

            {/* Social Login */}
            {/* <div className="mt-32 center-border-horizontal text-center">
              <span className="bg-base z-1 px-4">Or sign in with</span>
            </div>

            <div className="mt-32 d-flex align-items-center gap-3">
              <button
                type="button"
                className="fw-semibold text-primary-light py-16 px-24 w-50 border radius-12 text-md d-flex align-items-center justify-content-center gap-12 line-height-1 bg-hover-primary-50"
                disabled={loading}
              >
                <Icon
                  icon="ic:baseline-facebook"
                  className="text-primary-600 text-xl line-height-1"
                />
                Facebook
              </button>
              <button
                type="button"
                className="fw-semibold text-primary-light py-16 px-24 w-50 border radius-12 text-md d-flex align-items-center justify-content-center gap-12 line-height-1 bg-hover-primary-50"
                disabled={loading}
              >
                <Icon
                  icon="logos:google-icon"
                  className="text-primary-600 text-xl line-height-1"
                />
                Google
              </button>
            </div> */}

            {/* Sign Up Link */}
            {/* <div className="mt-32 text-center text-sm">
              <p className="mb-0">
                Don't have an account?{" "}
                <Link to="/sign-up" className="text-primary-600 fw-semibold">
                  Sign Up
                </Link>
              </p>
            </div> */}
          </form>
        </div>
      </div>
    </section>
  );
};

export default SignInLayer;