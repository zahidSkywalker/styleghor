# 🚀 Style Ghor E-commerce Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Backend Requirements
- [x] Django project with all models
- [x] SSL Commerz payment integration
- [x] Admin interface
- [x] API endpoints
- [x] Database migrations
- [x] Static files configuration

### ❌ Still Needed
- [ ] Real SSL Commerz credentials
- [ ] Production database setup
- [ ] Domain configuration
- [ ] SSL certificate setup

---

## 🌐 **Backend Deployment on Render**

### **Step 1: Prepare Your Code**
```bash
# Make sure build.sh is executable
chmod +x build.sh

# Commit all changes
git add .
git commit -m "Production ready for deployment"
git push origin main
```

### **Step 2: Deploy on Render**

1. **Go to [render.com](https://render.com)**
2. **Create New Account** (if you don't have one)
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service:**

   **Basic Settings:**
   - **Name:** `styleghor-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn styleghor.wsgi:application`

   **Environment Variables:**
   ```
   SECRET_KEY=your-generated-secret-key
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=postgresql://... (will be auto-generated)
   SSL_COMMERZ_STORE_ID=your_live_store_id
   SSL_COMMERZ_STORE_PASSWORD=your_live_store_password
   SSL_COMMERZ_SANDBOX=False
   ```

6. **Click "Create Web Service"**

### **Step 3: Database Setup**
1. **In your Render dashboard, click "New +" → "PostgreSQL"**
2. **Name:** `styleghor-db`
3. **Plan:** Free (or paid for production)
4. **Copy the connection string**
5. **Add to your web service environment variables:**
   ```
   DATABASE_URL=postgresql://... (paste connection string)
   ```

---

## 🎨 **Frontend Deployment on Vercel**

### **Option A: Deploy Django Templates (Current Setup)**

Since we're using Django templates, you can deploy the entire project on Render. The frontend is already integrated.

### **Option B: Separate Frontend (Advanced)**

If you want to create a separate React/Vue frontend:

1. **Create a new frontend project:**
   ```bash
   npx create-react-app styleghor-frontend
   # or
   npm create vue@latest styleghor-frontend
   ```

2. **Deploy to Vercel:**
   - Connect your GitHub repo
   - Vercel will auto-detect and deploy
   - Update CORS settings in Django backend

---

## 🔐 **SSL Commerz Production Setup**

### **Step 1: Get Live Credentials**
1. **Contact SSL Commerz support**
2. **Provide business documents**
3. **Get your live Store ID and Password**

### **Step 2: Update Environment Variables**
```bash
SSL_COMMERZ_STORE_ID=your_live_store_id
SSL_COMMERZ_STORE_PASSWORD=your_live_store_password
SSL_COMMERZ_SANDBOX=False
```

---

## 🌍 **Domain & SSL Setup**

### **Custom Domain on Render**
1. **In your web service dashboard**
2. **Go to "Settings" → "Custom Domains"**
3. **Add your domain (e.g., `api.styleghor.com`)**
4. **Update DNS records as instructed**

### **SSL Certificate**
- Render provides free SSL certificates automatically
- Just add your custom domain and SSL will be configured

---

## 📱 **Testing Your Deployment**

### **Backend Health Check**
```bash
# Test admin interface
curl https://your-backend.onrender.com/admin/

# Test API endpoints
curl https://your-backend.onrender.com/api/products/
```

### **Payment Testing**
1. **Use SSL Commerz sandbox first**
2. **Test with test cards**
3. **Switch to live when ready**

---

## 🚨 **Production Security Checklist**

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY`
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Database credentials secured
- [ ] Payment credentials secured
- [ ] Error logging enabled
- [ ] Regular backups configured

---

## 📊 **Monitoring & Maintenance**

### **Render Dashboard**
- Monitor service health
- View logs
- Check performance metrics

### **Database Monitoring**
- Monitor connection usage
- Check query performance
- Set up alerts for issues

---

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Build Failures:**
   - Check `requirements.txt`
   - Verify Python version
   - Check build logs

2. **Database Connection:**
   - Verify `DATABASE_URL`
   - Check PostgreSQL service status

3. **Static Files:**
   - Ensure `collectstatic` runs
   - Check WhiteNoise configuration

4. **Payment Issues:**
   - Verify SSL Commerz credentials
   - Check sandbox vs live mode

---

## 📞 **Support Resources**

- **Render Docs:** [docs.render.com](https://docs.render.com)
- **Vercel Docs:** [vercel.com/docs](https://vercel.com/docs)
- **SSL Commerz:** [developer.sslcommerz.com](https://developer.sslcommerz.com)
- **Django Docs:** [docs.djangoproject.com](https://docs.djangoproject.com)

---

## 🎯 **Next Steps After Deployment**

1. **Test all functionality**
2. **Set up monitoring**
3. **Configure backups**
4. **Set up CI/CD pipeline**
5. **Performance optimization**
6. **SEO optimization**
7. **Analytics integration**

---

**🎉 Congratulations! Your e-commerce site is now production-ready!**