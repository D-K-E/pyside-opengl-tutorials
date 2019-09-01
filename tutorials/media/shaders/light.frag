#version 330 core
in mediump vec3 Normal;
in mediump vec2 TexCoords;
in mediump vec3 FragPos;

out vec4 FragColor;

struct Material {
  sampler2D diffuseMap;  // object picture
  sampler2D specularMap; // normal map
  float shininess;
  float diffuse;
  float specular;
};

uniform Material material;

struct SpotLight {
  highp vec3 position;
  highp vec3 direction;

  highp vec3 ambientIntensity;
  highp vec3 diffuseIntensity;
};

uniform SpotLight light;

struct Coefficients {
  float lightCutOff;

  float ambient;

  float attrConstant;
  float attrLinear;
  float attrQuadratic;
};

uniform Coefficients coeffs;

uniform mediump vec3 viewerPosition;

void main(void) {
  vec3 objDiffuseColor = light.diffuseIntensity * texture(material.diffuseMap, TexCoords).rgb;
  vec3 objSpecularColor = light.diffuseIntensity * texture(material.specularMap, TexCoords).rgb;
  // ambient term I_a × k_a × O_d
  // I_a: ambient light intensity
  // k_a: ambient light coefficient
  // O_d: object's diffuse Color
  vec3 ambientTerm = light.ambientIntensity * objDiffuseColor * coeffs.ambient;

  vec3 lightDirection = normalize(light.position - FragPos);

  float theta = dot(lightDirection, normalize(-light.direction));
  if (theta > coeffs.lightCutOff){
    // lambertian terms k_d * O_d * (N \cdot L)
    // k_d: object diffuse reflection coefficient
    // N: normal to surface
    // L: direction of the light source
    // (N \cdot L): costheta
    vec3 norm = normalize(Normal);
    float costheta = dot(lightDirection, norm);
    costheta = max(costheta, 0.0);
    vec3 lambertianTerm = costheta * material.diffuse * objDiffuseColor;

    // expanding lambertian to phong

    // specular term k_s * O_s * (R \cdot V)^n
    // k_s: object specular coefficient
    // O_s: object specular color
    // R: reflection vector for direction of reflection
    // V: viewpoint or viewer direction
    // n: shininess
    vec3 viewerDirection = normalize(viewerPosition - FragPos);
    // R = 2 N * (N \cdot L) - L
    vec3 reflection =  reflect(-lightDirection, norm);
    reflection = normalize(reflection);
    float theta2 = dot(reflection, viewerDirection);
    vec3 specularTerm = material.specular * objSpecularColor * pow(theta2, 
    material.shininess);

    // attenuation term f_att
    float dist = length(light.position - FragPos);
    float attrQuad = coeffs.attrQuadratic * (dist * dist);
    float attrLinear = coeffs.attrLinear * dist;
    float attr = coeffs.attrConstant + attrQuad + attrLinear;
    float attenuation = min(1.0 / attr, 1.0);

    // f_att * I_p * (lambertianTerm + specularTerm)
    // I_p: light source intensity
    vec3 secondTerm = specularTerm + lambertianTerm;
    secondTerm = secondTerm * attenuation * light.diffuseIntensity;

    vec3 result = ambientTerm + secondTerm;
    FragColor = vec4(result, 1.0);
  }else{
    FragColor = vec4(light.ambientIntensity * objDiffuseColor, 1.0);
      }
}
