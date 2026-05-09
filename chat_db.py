from app import create_app, mongo
from datetime import datetime

app = create_app()

def init_chat_database():
    with app.app_context():
       
        
        # Medical Q&A Database
        # complete_medical_data.py

        # Comprehensive Medical Q&A Database
        qa_pairs = [
            # ==================== RESPIRATORY CONDITIONS ====================
            {
                'question': 'i have fever',
                'answer': '🌡️ **For Fever:**\n\n• Take Paracetamol (500mg) every 6 hours\n• Drink plenty of water and fluids\n• Rest and use cold compress on forehead\n• Monitor temperature every 4 hours\n\n⚠️ **See a doctor if:**\n• Fever above 103°F (39.4°C)\n• Fever lasts more than 3 days\n• Accompanied by severe headache or rash\n• Child under 3 months with any fever',
                'category': 'respiratory',
                'keywords': 'fever,temperature,high temp,hot body,feverish'
            },
            {
                'question': 'i have cold',
                'answer': '🤧 **For Common Cold:**\n\n• Take Cetirizine (10mg) for runny nose\n• Gargle with warm salt water for sore throat\n• Drink honey-lemon tea or warm fluids\n• Use cough drops or lozenges\n• Rest and stay hydrated\n• Use saline nasal drops for blocked nose\n\n⚠️ **See doctor if:**\n• Symptoms last >5 days\n• High fever develops\n• Difficulty breathing\n• Green/yellow mucus for >7 days',
                'category': 'respiratory',
                'keywords': 'cold,cough,sneeze,runny nose,sore throat,stuffy nose'
            },
            {
                'question': 'i have cough',
                'answer': '🍯 **For Cough Relief:**\n\n**Dry Cough:**\n• Honey with warm water\n• Cough suppressants (Dextromethorphan)\n• Lozenges or hard candy\n\n**Wet Cough (with mucus):**\n• Expectorants (Guaifenesin)\n• Steam inhalation\n• Warm fluids\n\n**Natural Remedies:**\n• Ginger tea with honey\n• Turmeric milk\n• Salt water gargle\n\n⚠️ **See doctor if:**\n• Cough lasts >3 weeks\n• Blood in mucus\n• Difficulty breathing\n• Chest pain',
                'category': 'respiratory',
                'keywords': 'cough,dry cough,wet cough,coughing'
            },
            {
                'question': 'i have sore throat',
                'answer': '🗣️ **For Sore Throat Relief:**\n\n• Gargle with warm salt water (4-5 times daily)\n• Drink warm honey lemon tea\n• Use throat lozenges or sprays\n• Stay hydrated with warm fluids\n• Rest your voice\n• Use a humidifier\n\n**Medicines:**\n• Paracetamol for pain\n• Throat sprays (Strepsils, Betadine)\n\n⚠️ **See doctor if:**\n• Severe pain\n• Difficulty swallowing\n• Fever >101°F\n• White patches on tonsils\n• Symptoms last >5 days',
                'category': 'respiratory',
                'keywords': 'sore throat,throat pain,painful swallowing,throat infection'
            },
            {
                'question': 'difficulty breathing',
                'answer': '🚨 **Difficulty Breathing - URGENT!** 🚨\n\n⚠️ **SEE A DOCTOR IMMEDIATELY IF:**\n• Shortness of breath at rest\n• Chest tightness or pain\n• Blue lips or fingernails\n• Wheezing or gasping\n• Can\'t speak full sentences\n\n**For mild breathing issues:**\n• Sit upright (don\'t lie down)\n• Use prescribed inhaler if available\n• Breathe slowly through pursed lips\n• Loosen tight clothing\n• Use a fan for air movement\n\n📞 **Call emergency: +91-XXXXXXXXXX**',
                'category': 'emergency',
                'keywords': 'breathing difficulty,shortness of breath,wheezing,gasping'
            },
            
            # ==================== PAIN CONDITIONS ====================
            {
                'question': 'i have headache',
                'answer': '🤕 **For Headache Relief:**\n\n**Tension Headache:**\n• Take Paracetamol (500mg) or Ibuprofen (400mg)\n• Rest in a dark, quiet room\n• Apply cold or warm compress\n• Gentle neck stretches\n\n**Migraine:**\n• Lie down in dark room\n• Cold compress on forehead\n• Avoid bright lights and loud noises\n• Prescription migraine medicine\n\n**Prevention:**\n• Stay hydrated\n• Regular sleep schedule\n• Avoid triggers (caffeine, stress)\n\n⚠️ **Emergency signs:**\n• Sudden severe headache (thunderclap)\n• Headache after head injury\n• With confusion, vision changes, or weakness',
                'category': 'pain',
                'keywords': 'headache,migraine,head pain,tension headache,cluster headache'
            },
            {
                'question': 'body pain',
                'answer': '💪 **For Body Pain Relief:**\n\n**Muscle Pain:**\n• Take Ibuprofen (400mg) or Paracetamol\n• Apply pain relief gel (Volini, Moov, Omnigel)\n• Rest the affected area\n• Use warm compress\n• Gentle stretching\n\n**Joint Pain:**\n• Apply ice for swelling, heat for stiffness\n• Rest and elevate if swollen\n• Over-the-counter pain relievers\n\n**Natural Remedies:**\n• Epsom salt bath\n• Massage with warm oil\n• Gentle yoga or stretching\n\n⚠️ **See doctor if:**\n• Severe or sudden pain\n• Accompanied by swelling or redness\n• Limited movement\n• Pain lasts >1 week',
                'category': 'pain',
                'keywords': 'body pain,muscle pain,joint pain,body ache,myalgia'
            },
            {
                'question': 'back pain',
                'answer': '🦴 **For Back Pain Relief:**\n\n**Acute Back Pain:**\n• Rest for 1-2 days (don\'t stay in bed longer)\n• Apply ice first 24-48 hours, then heat\n• Take Ibuprofen or Paracetamol\n• Maintain good posture\n• Sleep on side with pillow between knees\n\n**Stretches:**\n• Knee to chest stretch\n• Cat-cow stretch\n• Pelvic tilts\n\n⚠️ **See doctor if:**\n• Pain after injury or fall\n• Numbness in legs\n• Loss of bladder/bowel control\n• Fever with back pain\n• Pain radiates down leg\n• Unexplained weight loss',
                'category': 'pain',
                'keywords': 'back pain,lower back pain,spinal pain,lumbar pain'
            },
            {
                'question': 'neck pain',
                'answer': '🦒 **For Neck Pain Relief:**\n\n• Apply ice first 24 hours, then heat\n• Take Ibuprofen or Paracetamol\n• Gentle neck stretches\n• Maintain good posture\n• Use a supportive pillow\n• Avoid looking down at phone for long\n\n**Stretches:**\n• Chin tucks\n• Side-to-side rotation\n• Ear to shoulder stretch\n\n⚠️ **See doctor if:**\n• Pain after accident or fall\n• Numbness/tingling in arms\n• Severe headache with neck pain\n• Fever and stiff neck (possible meningitis)',
                'category': 'pain',
                'keywords': 'neck pain,cervical pain,stiff neck'
            },
            {
                'question': 'stomach pain',
                'answer': '🍽️ **For Stomach Pain:**\n\n**Upper Stomach Pain:**\n• Take antacids (Gelusil, Digene)\n• Avoid spicy and oily foods\n• Eat small, frequent meals\n• Drink warm water with ginger\n\n**Lower Stomach Pain:**\n• Rest and apply warm compress\n• Drink clear fluids\n• Avoid solid food for few hours\n\n**Gas/Acidity:**\n• Walk gently\n• Peppermint or chamomile tea\n• Avoid carbonated drinks\n\n⚠️ **Emergency signs:**\n• Severe, sudden pain\n• Blood in vomit or stool\n• Fever with chills\n• Unable to pass stool/gas\n• Pregnancy with pain\n• Recent abdominal injury',
                'category': 'digestive',
                'keywords': 'stomach pain,abdominal pain,belly pain,gastric pain'
            },
            
            # ==================== DIGESTIVE CONDITIONS ====================
            {
                'question': 'acidity',
                'answer': '🔥 **For Acidity Relief:**\n\n**Immediate Relief:**\n• Take antacids (Gelusil, Digene)\n• Drink cold milk\n• Eat banana or cold watermelon\n• Chew fennel seeds\n\n**Lifestyle Changes:**\n• Avoid spicy and oily food\n• Don\'t lie down immediately after eating\n• Eat smaller meals\n• Avoid caffeine and alcohol\n• Quit smoking\n\n**Long-term Prevention:**\n• Maintain healthy weight\n• Eat 2-3 hours before bedtime\n• Elevate head while sleeping\n• Reduce stress\n\n⚠️ **See doctor if:**\n• Acidity occurs frequently (>2 times/week)\n• Difficulty swallowing\n• Black/tarry stools\n• Unexplained weight loss',
                'category': 'digestive',
                'keywords': 'acidity,gas,heartburn,acid reflux,gerd'
            },
            {
                'question': 'nausea',
                'answer': '🤢 **For Nausea Relief:**\n\n**Immediate Relief:**\n• Eat small, bland foods (crackers, toast)\n• Drink ginger tea or lemon water\n• Avoid strong smells\n• Get fresh air\n• Sit upright, don\'t lie flat\n\n**Medicines:**\n• Antacids for acid-related nausea\n• Motion sickness bands\n• Prescription anti-nausea meds if severe\n\n**Natural Remedies:**\n• Peppermint tea\n• Ginger candies or chews\n• Cold compress on forehead\n\n⚠️ **See doctor if:**\n• Nausea lasts >2 days\n• Can\'t keep fluids down\n• Signs of dehydration\n• Severe abdominal pain\n• Head injury followed by nausea',
                'category': 'digestive',
                'keywords': 'nausea,feeling sick,queasy,upset stomach'
            },
            {
                'question': 'vomiting',
                'answer': '🤮 **For Vomiting:**\n\n**Immediate Care:**\n• Stop eating solid food\n• Sip clear fluids slowly (water, ORS)\n• Rest sitting up\n• Don\'t lie flat\n\n**After vomiting stops:**\n• Start with small sips of water\n• Try BRAT diet (Banana, Rice, Apple sauce, Toast)\n• Avoid dairy, spicy, fatty foods\n• Gradually return to normal diet\n\n**Oral Rehydration Solution (ORS):**\n• 1 liter water + 6 tsp sugar + 1/2 tsp salt\n\n⚠️ **Emergency signs:**\n• Blood in vomit (red or coffee-ground)\n• Severe headache or stiff neck\n• Can\'t keep fluids down for 12 hours\n• Signs of dehydration (dry mouth, no urine)\n• After head injury\n• Green vomit (bile)',
                'category': 'digestive',
                'keywords': 'vomiting,throwing up,emesis'
            },
            {
                'question': 'diarrhea',
                'answer': '💩 **For Diarrhea Management:**\n\n**Immediate Care:**\n• Drink plenty of fluids (water, ORS, clear broths)\n• Avoid dairy, fatty, spicy foods\n• Eat BRAT diet (Banana, Rice, Apple sauce, Toast)\n• Rest and stay near bathroom\n\n**Medicines:**\n• ORS for hydration\n• Probiotics (yogurt, supplements)\n• Loperamide for adults only (not for children)\n\n**What to eat:**\n• Clear liquids\n• Saltine crackers\n• Boiled potatoes\n• Steamed rice\n\n⚠️ **See doctor if:**\n• Diarrhea lasts >3 days\n• Blood or mucus in stool\n• Severe abdominal pain\n• Fever >102°F\n• Signs of dehydration\n• Child or elderly with diarrhea',
                'category': 'digestive',
                'keywords': 'diarrhea,loose motion,loose stools,food poisoning'
            },
            {
                'question': 'constipation',
                'answer': '💩 **For Constipation Relief:**\n\n**Immediate Relief:**\n• Drink warm water with lemon\n• Eat high-fiber foods (prunes, figs, bran)\n• Gentle abdominal massage\n• Light exercise (walking)\n\n**Lifestyle Changes:**\n• Drink 8-10 glasses of water daily\n• Eat more fruits and vegetables\n• Exercise regularly\n• Don\'t ignore urge to go\n\n**Natural Laxatives:**\n• Prunes or prune juice\n• Flaxseeds (soaked overnight)\n• Aloe vera juice\n\n**Medicines (short-term only):**\n• Fiber supplements (Psyllium)\n• Stool softeners (Docusate)\n• Osmotic laxatives (Lactulose)\n\n⚠️ **See doctor if:**\n• No bowel movement for 3+ days\n• Severe abdominal pain\n• Blood in stool\n• Unexplained weight loss\n• Alternating constipation and diarrhea',
                'category': 'digestive',
                'keywords': 'constipation,hard stool,difficulty pooping,irregular bowel'
            },
            
            # ==================== SKIN CONDITIONS ====================
            {
                'question': 'rash',
                'answer': '🔴 **For Skin Rash:**\n\n**General Care:**\n• Keep area clean and dry\n• Apply calamine lotion for itching\n• Use fragrance-free moisturizer\n• Avoid scratching\n• Wear loose, cotton clothing\n\n**For Allergic Rash:**\n• Take antihistamine (Cetirizine)\n• Apply hydrocortisone cream\n• Avoid known allergens\n\n**For Heat Rash:**\n• Stay in cool environment\n• Take cool showers\n• Wear breathable fabrics\n\n⚠️ **See doctor if:**\n• Rash with fever\n• Blisters or open sores\n• Spreads rapidly\n• Painful rash\n• Rash around eyes or mouth\n• Difficulty breathing\n• Rash after new medication',
                'category': 'skin',
                'keywords': 'rash,skin rash,hives,itchy skin,red spots'
            },
            {
                'question': 'itching',
                'answer': '🖐️ **For Itching Relief:**\n\n**Immediate Relief:**\n• Apply cold compress\n• Take cool bath with oatmeal\n• Use calamine lotion\n• Apply moisturizer\n• Keep nails short\n\n**Medicines:**\n• Antihistamines (Cetirizine, Loratadine)\n• Hydrocortisone cream for localized itch\n\n**Natural Remedies:**\n• Aloe vera gel\n• Coconut oil\n• Baking soda paste\n• Apple cider vinegar (diluted)\n\n**Avoid:**\n• Hot showers\n• Scratching\n• Tight or synthetic clothing\n• Harsh soaps\n\n⚠️ **See doctor if:**\n• Itching all over body\n• No obvious cause\n• Interferes with sleep\n• Accompanied by jaundice\n• During pregnancy',
                'category': 'skin',
                'keywords': 'itching,pruritus,itchy skin,scratching'
            },
            {
                'question': 'acne',
                'answer': '🌟 **For Acne Treatment:**\n\n**Mild Acne:**\n• Wash face twice daily with gentle cleanser\n• Use benzoyl peroxide or salicylic acid\n• Apply oil-free moisturizer\n• Don\'t pop pimples\n\n**Moderate Acne:**\n• Topical antibiotics (clindamycin)\n• Retinoids (adapalene)\n• Azelaic acid\n\n**Prevention:**\n• Keep skin clean\n• Avoid touching face\n• Change pillowcases frequently\n• Reduce dairy and sugar\n• Stay hydrated\n\n**Home Remedies:**\n• Tea tree oil (diluted)\n• Green tea toner\n• Aloe vera gel\n\n⚠️ **See dermatologist if:**\n• Severe or cystic acne\n• Scarring\n• Over-the-counter not working\n• Acne affecting self-esteem',
                'category': 'skin',
                'keywords': 'acne,pimples,breakouts,zits'
            },
            
            # ==================== EYE CONDITIONS ====================
            {
                'question': 'eye pain',
                'answer': '👁️ **For Eye Pain:**\n\n**Common Causes & Relief:**\n\n**Eye Strain:**\n• Rest eyes (20-20-20 rule: every 20 min, look 20 feet away for 20 sec)\n• Use artificial tears\n• Adjust screen brightness\n\n**Dry Eyes:**\n• Use lubricating eye drops\n• Blink frequently\n• Use humidifier\n\n**Foreign Object:**\n• Blink repeatedly\n• Rinse with clean water\n• Don\'t rub\n\n⚠️ **Emergency signs:**\n• Sudden vision changes\n• Severe pain\n• Eye injury or chemical exposure\n• Light sensitivity\n• Redness with discharge\n• Foreign body stuck in eye',
                'category': 'eye',
                'keywords': 'eye pain,sore eyes,eye discomfort,eye strain'
            },
            {
                'question': 'pink eye',
                'answer': '👁️ **For Conjunctivitis (Pink Eye):**\n\n**Symptoms:** Redness, itching, discharge, tearing\n\n**Viral Pink Eye:**\n• Usually resolves on its own (7-14 days)\n• Apply cold compresses\n• Use artificial tears\n• Wash hands frequently\n\n**Bacterial Pink Eye:**\n• Antibiotic eye drops (prescription)\n• Warm compresses\n• Clean discharge gently\n\n**Allergic Pink Eye:**\n• Antihistamine eye drops\n• Avoid allergens\n• Cold compresses\n\n**Prevention:**\n• Don\'t share towels/pillows\n• Wash hands often\n• Avoid touching eyes\n• Stay home from work/school\n\n⚠️ **See doctor if:**\n• Severe pain\n• Vision changes\n• Light sensitivity\n• Newborn with pink eye\n• Symptoms not improving in 3 days',
                'category': 'eye',
                'keywords': 'pink eye,conjunctivitis,red eye,eye infection'
            },
            
            # ==================== EAR CONDITIONS ====================
            {
                'question': 'ear pain',
                'answer': '👂 **For Ear Pain:**\n\n**Immediate Relief:**\n• Apply warm compress\n• Take pain reliever (Paracetamol, Ibuprofen)\n• Sleep with head elevated\n• Chew gum or yawn to equalize pressure\n\n**For Ear Infection:**\n• See doctor for antibiotics if bacterial\n• Over-the-counter ear drops for pain\n\n**For Swimmer\'s Ear:**\n• Keep ear dry\n• Over-the-counter acetic acid drops\n\n**Prevention:**\n• Dry ears after swimming\n• Avoid inserting objects in ear\n• Treat allergies\n\n⚠️ **See doctor if:**\n• Severe pain\n• Discharge from ear\n• Hearing loss\n• Fever\n• Dizziness\n• Pain after injury\n• Child under 6 months',
                'category': 'ear',
                'keywords': 'ear pain,earache,ear infection,otalgia'
            },
            
            # ==================== URINARY CONDITIONS ====================
            {
                'question': 'urine infection',
                'answer': '💧 **For Urinary Tract Infection (UTI):**\n\n**Symptoms:** Burning with urination, frequent urge, cloudy/foul urine\n\n**Immediate Care:**\n• Drink plenty of water\n• Urinate frequently\n• Take over-the-counter pain relievers\n• Use heating pad for pain\n\n**Natural Remedies:**\n• Unsweetened cranberry juice\n• D-mannose supplements\n• Probiotics\n\n**Medical Treatment:**\n• Antibiotics (prescription only)\n• Urinary analgesics (for pain)\n\n**Prevention:**\n• Wipe front to back\n• Urinate after intercourse\n• Stay hydrated\n• Avoid irritants (caffeine, alcohol)\n\n⚠️ **See doctor if:**\n• First UTI\n• Fever or chills\n• Back pain\n• Blood in urine\n• Pregnant\n• Symptoms severe\n• Recurring UTIs',
                'category': 'urinary',
                'keywords': 'uti,urine infection,bladder infection,urinary tract infection'
            },
            
            # ==================== ALLERGIES ====================
            {
                'question': 'allergy',
                'answer': '🤧 **For Allergies:**\n\n**Common Symptoms:** Sneezing, runny nose, itchy eyes, rash\n\n**Immediate Relief:**\n• Take antihistamines (Cetirizine, Loratadine, Fexofenadine)\n• Use nasal sprays for congestion\n• Apply cold compress for itchy eyes\n\n**Environmental Allergies:**\n• Keep windows closed during high pollen\n• Use air purifier\n• Shower after being outdoors\n• Wash bedding in hot water weekly\n\n**Food Allergies:**\n• Avoid trigger foods\n• Carry epinephrine if prescribed\n• Read food labels carefully\n\n⚠️ **EMERGENCY (Anaphylaxis):**\n• Difficulty breathing\n• Swelling of throat/tongue\n• Rapid pulse\n• Dizziness or fainting\n• Hives all over body\n\n📞 **Call emergency immediately if above signs!**',
                'category': 'allergy',
                'keywords': 'allergy,allergic reaction,hay fever,pollen allergy,food allergy'
            },
            
            # ==================== MEDICINES ====================
            {
                'question': 'medicine for fever',
                'answer': '💊 **Medicine for Fever:**\n\n**Adults:**\n• **Paracetamol (Crocin, Dolo 650)** - 500-650mg every 6 hours\n• **Ibuprofen (Brufen)** - 400mg every 8 hours\n• **Aspirin** - For adults only (not for children)\n\n**Children:**\n• **Paracetamol drops/syrup** - Dose by weight\n• **Ibuprofen syrup** - For children >6 months\n\n**Natural Fever Reducers:**\n• Lukewarm sponge bath\n• Stay hydrated\n• Rest\n\n⚠️ **Important:**\n• Don\'t exceed recommended dose\n• Don\'t combine Paracetamol and Ibuprofen without doctor advice\n• Don\'t give aspirin to children under 18\n• Consult doctor for persistent fever',
                'category': 'medicines',
                'keywords': 'fever medicine,fever tablet,paracetamol,ibuprofen'
            },
            {
                'question': 'medicine for cold',
                'answer': '💊 **Medicine for Cold:**\n\n**Runny Nose/Sneezing:**\n• **Cetirizine (Cetzine)** - 10mg once daily\n• **Loratadine (Lorfast)** - 10mg once daily\n• **Chlorpheniramine** - 4mg every 4-6 hours (causes drowsiness)\n\n**Cough:**\n• **Dry cough:** Dextromethorphan (Benadryl Dry Cough)\n• **Wet cough:** Guaifenesin (Expectorant)\n• **Cough syrup (Benadryl, Corex, Ascoril)**\n\n**Blocked Nose:**\n• **Nasal drops (Otrivin, Nasivion)** - Short-term use only\n• **Saline nasal spray** - Safe for frequent use\n\n**Sore Throat:**\n• **Throat lozenges (Strepsils, Vicks)**\n• **Throat spray (Betadine)**\n\n**Combination Medicines:**\n• Sinarest, Coldact, Alex (contain multiple ingredients)\n\n⚠️ **Read labels carefully!** Many cold medicines contain Paracetamol - don\'t double dose!',
                'category': 'medicines',
                'keywords': 'cold medicine,cold tablet,cough medicine,sinarest,cetirizine'
            },
            {
                'question': 'medicine for headache',
                'answer': '💊 **Medicine for Headache:**\n\n**For Tension Headache:**\n• **Paracetamol (Crocin, Dolo 650)** - 500-650mg\n• **Ibuprofen (Brufen)** - 400mg\n• **Aspirin (Disprin)** - 300-600mg (adults only)\n\n**For Migraine:**\n• **Ibuprofen** or **Naproxen**\n• **Sumatriptan** (prescription only)\n• **Combination (Excedrin Migraine)** - Aspirin + Paracetamol + Caffeine\n\n**Natural Options:**\n• Caffeine (in small amounts)\n• Magnesium supplements\n• Ginger tea\n\n⚠️ **Don\'t take:**\n• Don\'t exceed 4000mg Paracetamol/day\n• Don\'t take aspirin if under 18\n• Avoid painkiller overuse (can cause rebound headaches)\n\n**See doctor if:**\n• Headaches frequent (>2/week)\n• Medicines not helping\n• New type of headache after 50',
                'category': 'medicines',
                'keywords': 'headache medicine,headache tablet,migraine medicine'
            },
            {
                'question': 'medicine for stomach pain',
                'answer': '💊 **Medicine for Stomach Issues:**\n\n**Acidity/Gas:**\n• **Antacids (Gelusil, Digene)** - Chewable tablets\n• **Ranitidine** - Reduces acid (prescription in some countries)\n• **Omeprazole (Omez)** - For GERD (prescription)\n• **Simethicone** - For gas relief\n\n**Stomach Cramps:**\n• **Dicyclomine (Cyclopam)** - For smooth muscle spasms\n• **Hyoscine (Buscopan)** - For abdominal cramps\n\n**Nausea/Vomiting:**\n• **Domperidone** - For nausea\n• **Ondansetron** - Prescription for severe nausea\n• **Ginger capsules** - Natural option\n\n**Diarrhea:**\n• **ORS** - For hydration (most important!)\n• **Probiotics** - Restore gut bacteria\n• **Loperamide** - For adults only\n\n**Natural Options:**\n• Peppermint oil capsules (for IBS)\n• Ginger tea for nausea\n• Fennel seeds for gas\n\n⚠️ **Important:**\n• Most stomach medicines should not be taken long-term\n• See doctor for persistent symptoms\n• Antacids can interfere with other medicines',
                'category': 'medicines',
                'keywords': 'stomach medicine,antacids,gas medicine,acidity medicine'
            },
            {
                'question': 'medicine for pain',
                'answer': '💊 **Pain Relievers Guide:**\n\n**Mild Pain:**\n• **Paracetamol (Crocin, Dolo 650)** - Safe for most, gentle on stomach\n\n**Moderate Pain:**\n• **Ibuprofen (Brufen)** - Anti-inflammatory, good for muscle/joint pain\n• **Naproxen (Naprosyn)** - Longer-lasting, for arthritis\n\n**Moderate-Severe Pain:**\n• **Combination (Paracetamol + Ibuprofen)** - Alternating every 4-6 hours\n• **Aspirin** - For pain with inflammation (adults only)\n\n**Neuropathic Pain (nerve pain):**\n• **Gabapentin** - Prescription only\n• **Pregabalin** - Prescription only\n\n**Topical (for localized pain):**\n• **Diclofenac gel (Volini, Voveran)** - For joint/muscle pain\n• **Capsaicin cream** - For arthritis\n• **Lidocaine patches** - For localized pain\n\n⚠️ **Painkiller Safety:**\n• Don\'t exceed recommended dose\n• Don\'t combine multiple products with Paracetamol\n• Avoid NSAIDs (Ibuprofen, Naproxen) if stomach issues\n• See doctor for chronic pain',
                'category': 'medicines',
                'keywords': 'pain medicine,painkiller,analgesic'
            },
            
            # ==================== APPOINTMENTS & SERVICES ====================
            {
                'question': 'book appointment',
                'answer': '📅 **To Book an Appointment:**\n\n**Online Booking:**\n1️⃣ Go to **Appointments** section in sidebar\n2️⃣ Click **"New Appointment"**\n3️⃣ Select **Doctor** from the list\n4️⃣ Choose **Date and Time**\n5️⃣ Enter **Patient details**\n6️⃣ Click **"Confirm Booking"**\n\n**By Phone:**\n📞 Call reception: +91-XXXXXXXXXX\n\n**In Person:**\nVisit the hospital reception desk\n\n**Information needed:**\n• Patient name and age\n• Preferred doctor/department\n• Preferred date and time\n• Contact number\n\n✅ You\'ll receive confirmation via SMS/email',
                'category': 'services',
                'keywords': 'appointment,book appointment,schedule appointment,doctor appointment'
            },
            {
                'question': 'hospital timings',
                'answer': '🏥 **Hospital Operating Hours:**\n\n**Emergency Department:**\n• 24 hours, 7 days a week\n\n**Outpatient Department (OPD):**\n• Monday - Saturday: 9:00 AM - 5:00 PM\n• Sunday: Closed (Emergency only)\n• Lunch Break: 1:00 PM - 2:00 PM\n\n**Pharmacy:**\n• 24 hours, 7 days a week\n\n**Laboratory:**\n• Monday - Sunday: 7:00 AM - 9:00 PM\n\n**Visiting Hours:**\n• Evening: 4:00 PM - 6:00 PM\n• Morning: 11:00 AM - 12:00 PM\n\n**Emergency:** Always open\n\n📞 For after-hours emergencies: +91-XXXXXXXXXX',
                'category': 'information',
                'keywords': 'timings,hospital hours,opd timings,visiting hours'
            },
            {
                'question': 'consultation fee',
                'answer': '💰 **Consultation Fees:**\n\n**General Physician:**\n• ₹500 for first visit\n• ₹400 for follow-up\n\n**Specialist Doctor:**\n• ₹1000 for first visit\n• ₹800 for follow-up\n\n**Senior Specialist:**\n• ₹1500 - ₹2000\n\n**Emergency Consultation:**\n• ₹1000\n\n**Home Visit:**\n• ₹2000+ (depending on location)\n\n**Pediatrician (Child Specialist):**\n• ₹800\n\n**Gynecologist:**\n• ₹1000\n\n💳 **Payment Methods:** Cash, Card, UPI, Insurance\n\n**Free Services:**\n• Blood pressure check\n• Basic first aid\n• Health advice over phone',
                'category': 'financial',
                'keywords': 'fee,cost,price,consultation charge,doctor fee'
            },
            
            # ==================== EMERGENCY ====================
            {
                'question': 'emergency',
                'answer': '🚨 **EMERGENCY SERVICES** 🚨\n\n📞 **Emergency Helpline:** +91-XXXXXXXXXX\n🚑 **Ambulance:** +91-XXXXXXXXXX\n📍 **Emergency Room:** 24/7 - Main Building, Ground Floor\n\n**Go to ER immediately for:**\n• Chest pain or pressure\n• Difficulty breathing\n• Severe bleeding that won\'t stop\n• Loss of consciousness\n• Severe allergic reaction (swelling, trouble breathing)\n• Head injury with confusion\n• Sudden severe headache\n• Stroke signs (face drooping, arm weakness, speech difficulty)\n• Seizures\n• Severe burns\n• Poisoning or overdose\n\n**What to bring:**\n• ID proof\n• Insurance card (if any)\n• List of medications\n• Known allergies\n\n**Don\'t drive yourself - call ambulance!**\n\n📞 **For non-emergencies, call reception: +91-XXXXXXXXXX**',
                'category': 'emergency',
                'keywords': 'emergency,urgent,critical,accident,er'
            },
            
            # ==================== PREGNANCY ====================
            {
                'question': 'pregnancy symptoms',
                'answer': '🤰 **Early Pregnancy Symptoms:**\n\n**Common Signs:**\n• Missed period\n• Nausea (morning sickness)\n• Breast tenderness\n• Fatigue\n• Frequent urination\n• Food aversions or cravings\n• Mood swings\n• Bloating\n\n**When to take a test:**\n• First day of missed period\n• Home pregnancy test (99% accurate)\n\n**What to do:**\n• Start prenatal vitamins (folic acid)\n• Schedule first prenatal visit (8-10 weeks)\n• Avoid alcohol, smoking, certain medications\n• Eat healthy, balanced diet\n\n⚠️ **See doctor immediately if:**\n• Severe abdominal pain\n• Heavy bleeding\n• Severe vomiting (can\'t keep fluids down)\n• Severe headache with vision changes\n• Fever\n\n📅 Book an appointment with our Gynecology department!',
                'category': 'pregnancy',
                'keywords': 'pregnancy,pregnant,expecting,antenatal'
            },
            
            # ==================== CHILDREN ====================
            {
                'question': 'child fever',
                'answer': '👶 **Fever in Children:**\n\n**By age:**\n• Under 3 months: Any fever (100.4°F/38°C+) = EMERGENCY!\n• 3-6 months: Fever over 101°F (38.3°C) - call doctor\n• 6+ months: Fever over 103°F (39.4°C)\n\n**Medicine dosing (by weight, NOT age):**\n• Paracetamol (infant drops): Every 6 hours\n• Ibuprofen (for >6 months): Every 8 hours\n\n**Home care:**\n• Remove extra clothing\n• Lukewarm sponge bath (not cold)\n• Encourage fluids (breastmilk, formula, water, ORS)\n• Keep comfortable, not shivering\n\n**Warning signs (see doctor immediately):**\n• Fever with rash\n• Difficulty waking up\n• Not drinking liquids\n• Seizures\n• Difficulty breathing\n• Inconsolable crying\n• Stiff neck\n\n⚠️ **NEVER give aspirin to children!**',
                'category': 'pediatric',
                'keywords': 'child fever,baby fever,toddler fever'
            },
            
            # ==================== GENERAL ====================
            {
                'question': 'help',
                'answer': '🤖 **I can help you with:**\n\n🩺 **Medical Symptoms:**\n• Fever, cold, cough, sore throat\n• Headache, body pain, back pain\n• Stomach pain, acidity, diarrhea, constipation\n• Rash, itching, skin problems\n• Eye pain, ear pain\n• Urinary infection\n• Allergies\n\n💊 **Medicines:**\n• Medicine for fever, cold, headache\n• Medicine for pain, stomach issues\n• Proper dosage information\n\n📅 **Hospital Services:**\n• Book, cancel, reschedule appointments\n• Doctor information and availability\n• Hospital timings and visiting hours\n• Consultation fees and payment methods\n\n🚨 **Emergency:**\n• Emergency numbers\n• When to go to ER\n• First aid guidance\n\n🤰 **Special Cases:**\n• Pregnancy symptoms and care\n• Children\'s health\n\n**Just type your question naturally, and I\'ll help!**\n\n📞 For urgent matters, call: +91-XXXXXXXXXX',
                'category': 'general',
                'keywords': 'help,support,assistance,what can you do'
            },
        ]
        
        
        
        print("\n📊 Total documents in DB:",
            mongo.db.chat_knowledge.count_documents({}))
        print(f"\n📋 Categories included:")
        print(f"   • Respiratory conditions (fever, cold, cough, etc.)")
        print(f"   • Pain conditions (headache, body pain, back pain, etc.)")
        print(f"   • Digestive conditions (acidity, nausea, diarrhea, etc.)")
        print(f"   • Skin conditions (rash, itching, acne)")
        print(f"   • Eye & ear conditions")
        print(f"   • Urinary conditions")
        print(f"   • Allergies")
        print(f"   • Medicines guide")
        print(f"   • Pregnancy & children")
        print(f"   • Emergency services")
        print(f"   • Hospital services")



        # Insert Q&A pairs
        for qa in qa_pairs:

            existing = mongo.db.chat_knowledge.find_one({
                "question": qa["question"]
            })

            if not existing:
                qa["created_at"] = datetime.utcnow()
                qa["usage_count"] = 0
                qa["is_active"] = True

                mongo.db.chat_knowledge.insert_one(qa)
                print("✅ Inserted:", qa["question"])
            else:
                print("⚠️ Already exists:", qa["question"])

        print("\n🎉 Chat database initialized successfully!")


if __name__ == "__main__":
    init_chat_database()