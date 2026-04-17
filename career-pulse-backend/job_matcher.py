def calculate_match_score(job_description, job_title, user_skills):
    if not user_skills:
        return 0, []
    text = (str(job_description) + " " + str(job_title)).lower()
    matched_skills = []
    for skill in user_skills:
        if skill.lower() in text:
            matched_skills.append(skill)
    score = (len(matched_skills) / len(user_skills)) * 100
    return round(score, 1), matched_skills

def filter_and_sort_jobs(jobs_df, user_skills, min_score=20):
    if jobs_df.empty or not user_skills:
        return []
    results = []
    for _, job in jobs_df.iterrows():
        score, matched = calculate_match_score(job['description'], job['title'], user_skills)
        if score >= min_score:
            job_dict = job.to_dict()
            job_dict['match_score'] = score
            job_dict['matched_skills'] = matched
            results.append(job_dict)
    return sorted(results, key=lambda x: x['match_score'], reverse=True)[:15]
