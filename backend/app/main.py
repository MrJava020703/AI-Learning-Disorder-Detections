from pathlib import Path
import shutil, uuid
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .database import Base,engine,get_db
from .models import User,Student,Assessment,HandwritingSample
from .schemas import Register,Login,Token,StudentIn,AssessmentIn,OCRText
from .security import hash_password,verify_password,create_token,current_user
from .services import analyze_text,predict,ocr_image
from .core import settings
app=FastAPI(title='LearnSight AI API',version='1.0.0',description='AI-assisted learning-difficulty screening. Not a clinical diagnosis.')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(','),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def boot():
 Base.metadata.create_all(engine); db=next(get_db())
 if not db.query(User).filter_by(email='admin@learnsight.demo').first():
  admin=User(name='Demo Administrator',email='admin@learnsight.demo',password_hash=hash_password('DemoPass123!'),role='admin');db.add(admin);db.flush()
  s=Student(owner_id=admin.id,name='Aarav Sharma (Synthetic)',age=9,gender='Male',grade='4',school='Demo Public School',language='English',guardian_name='Synthetic Parent');db.add(s);db.flush()
  n=analyze_text('I like to read but sometimess words look the same same.');p=predict({'reading_difficulty':3,'letter_confusion':3,'spelling_difficulty':3,'comprehension_difficulty':2,'spacing_irregularity':2,'letter_formation':2,'writing_fatigue':2,'alignment_difficulty':1},'','',n)
  db.add(Assessment(student_id=s.id,questionnaire={},writing_text='I like to read but sometimess words look the same same.',nlp_result=n,**p));db.commit()
 db.close()
@app.get('/api/health')
def health(): return {'status':'healthy','screening_notice':'Not a clinical diagnosis'}
@app.post('/api/auth/register',response_model=Token)
def register(p:Register,db:Session=Depends(get_db)):
 if db.query(User).filter_by(email=p.email).first(): raise HTTPException(409,'An account with this email already exists')
 u=User(name=p.name,email=p.email,password_hash=hash_password(p.password),role=p.role);db.add(u);db.commit();db.refresh(u);return token(u)
@app.post('/api/auth/login',response_model=Token)
def login(p:Login,db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=p.email).first()
 if not u or not verify_password(p.password,u.password_hash): raise HTTPException(401,'Incorrect email or password')
 return token(u)
def token(u): return {'access_token':create_token(u),'user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}}
@app.get('/api/auth/me')
def me(u:User=Depends(current_user)): return {'id':u.id,'name':u.name,'email':u.email,'role':u.role}
@app.get('/api/students')
def students(db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=db.query(Student) if u.role=='admin' else db.query(Student).filter_by(owner_id=u.id)
 return [{'id':s.id,'name':s.name,'age':s.age,'gender':s.gender,'grade':s.grade,'school':s.school,'language':s.language,'assessment_count':len(s.assessments)} for s in q.order_by(Student.created_at.desc()).all()]
@app.post('/api/students')
def create_student(p:StudentIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=Student(owner_id=u.id,**p.model_dump());db.add(s);db.commit();db.refresh(s);return {'id':s.id,'name':s.name}
@app.get('/api/students/{id}')
def student_detail(id:int,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=owned_student(id,db,u);return {'id':s.id,'name':s.name,'age':s.age,'grade':s.grade,'school':s.school,'language':s.language,'assessments':[serialize(a) for a in s.assessments]}
def owned_student(id,db,u):
 s=db.get(Student,id)
 if not s or (s.owner_id!=u.id and u.role!='admin'): raise HTTPException(404,'Student not found')
 return s
def serialize(a): return {'id':a.id,'student_id':a.student_id,'dyslexia_score':a.dyslexia_score,'dysgraphia_score':a.dysgraphia_score,'overall_risk':a.overall_risk,'risk_level':a.risk_level,'confidence':a.confidence,'indicators':a.indicators,'nlp_result':a.nlp_result,'created_at':a.created_at}
@app.post('/api/assessments')
def create_assessment(p:AssessmentIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=owned_student(p.student_id,db,u);n=analyze_text(p.writing_text);r=predict(p.questionnaire,p.reading_text,p.writing_text,n);a=Assessment(student_id=s.id,questionnaire=p.questionnaire,reading_text=p.reading_text,writing_text=p.writing_text,nlp_result=n,**r);db.add(a);db.commit();db.refresh(a);return serialize(a)
@app.post('/api/nlp/analyze')
def nlp(p:OCRText,u:User=Depends(current_user)): return analyze_text(p.text)
@app.get('/api/prediction/{id}')
def prediction(id:int,db:Session=Depends(get_db),u:User=Depends(current_user)):
 a=db.get(Assessment,id)
 if not a or (a.student.owner_id!=u.id and u.role!='admin'): raise HTTPException(404,'Assessment not found')
 return dict(serialize(a),student_name=a.student.name)
@app.post('/api/upload/handwriting')
async def upload(assessment_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),u:User=Depends(current_user)):
 a=db.get(Assessment,assessment_id)
 if not a or (a.student.owner_id!=u.id and u.role!='admin'): raise HTTPException(404,'Assessment not found')
 if file.content_type not in {'image/jpeg','image/png','image/jpg'}: raise HTTPException(415,'Only JPG and PNG handwriting images are accepted')
 dest=Path(settings.upload_dir)/f'{uuid.uuid4().hex}_{file.filename}'
 with dest.open('wb') as out: shutil.copyfileobj(file.file,out)
 if dest.stat().st_size>settings.max_upload_mb*1024*1024: dest.unlink();raise HTTPException(413,'File exceeds upload limit')
 try: text=ocr_image(dest);error=None
 except RuntimeError as e: text='';error=str(e)
 db.add(HandwritingSample(assessment_id=a.id,filename=str(dest),ocr_text=text));db.commit();return {'filename':dest.name,'ocr_text':text,'nlp':analyze_text(text),'ocr_warning':error}
@app.get('/api/dashboard/statistics')
def stats(db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=db.query(Assessment).join(Student)
 if u.role!='admin': q=q.filter(Student.owner_id==u.id)
 rows=q.order_by(Assessment.created_at.desc()).all();total=len(rows);low=sum(x.risk_level=='Low' for x in rows);moderate=sum(x.risk_level=='Moderate' for x in rows);high=sum(x.risk_level=='High' for x in rows)
 return {'total_assessments':total,'students_assessed':len({x.student_id for x in rows}),'low':low,'moderate':moderate,'high':high,'average_risk':round(sum(x.overall_risk for x in rows)/max(1,total),1),'recent':[dict(serialize(x),student_name=x.student.name) for x in rows[:6]],'distribution':[{'name':'Low','value':low},{'name':'Moderate','value':moderate},{'name':'High','value':high}]}
@app.get('/api/reports/{id}')
def report(id:int,db:Session=Depends(get_db),u:User=Depends(current_user)):
 a=db.get(Assessment,id)
 if not a or (a.student.owner_id!=u.id and u.role!='admin'): raise HTTPException(404,'Assessment not found')
 path=Path('../reports')/f'LearnSight_Report_{a.id}.pdf';c=canvas.Canvas(str(path),pagesize=A4);y=790
 lines=['LearnSight AI — Screening Report','IMPORTANT: AI-assisted early screening only. Not a clinical diagnosis.',f'Student: {a.student.name} | Grade: {a.student.grade}',f'Assessment date: {a.created_at:%d %b %Y}',f'Dyslexia risk: {a.dyslexia_score}% | Dysgraphia risk: {a.dysgraphia_score}%',f'Overall learning difficulty risk: {a.overall_risk}% ({a.risk_level})',f'Confidence: {a.confidence*100:.0f}%','','Potential indicators:']+[f'- {x}' for x in a.indicators]+['','Recommended next step: Discuss high or persistent indicators with a qualified educator or clinician.']
 for line in lines: c.drawString(45,y,line[:115]);y-=24
 c.save();return FileResponse(path,media_type='application/pdf',filename=path.name)
