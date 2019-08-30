varying mediump vec3 Normal;
varying mediump vec3 TexCoords;
varying mediump vec3 FragPos;

struct Material {
  sampler2D diffuseMap; // object picture
  sampler2D specularMap; // normal map
  float shininess;
}

uniform Material material;

struct SpotLight {
  highp vec3 position;
  highp vec3 direction;

  highp vec3 ambient;
  highp vec3 diffuse;
  highp vec3 specular;
}

uniform SpotLight light;

struct Coefficients {
  float lightCutOff;

  float ambient;
  float diffuse;
  float specular;

  float attrConstant;
  float attrLinear;
  float attrQuadratic;
}

uniform Coefficients coeffs;

uniform mediump vec3 viewerPosition;

void main(void) {
  // normalize normals
  vec3 norm = normalize(Normal);
  vec3 lightDirection = normalize(light.position - FragPos);

  float dist = length(light.position - FragPos);
  float attrQuad = coeffs.attrQuadratic * (dist * dist);
  float attrLinear = coeffs.attrLinear * dist;
  float attr = coeffs.attrConstant + attrQuad + attrLinear;
  float attenuation = min(1.0 / attr, 1.0);

  float theta = dot(lightDirection, normalize(-light.direction));

  if (theta > coeffs.lightCutOff) {
    float costheta = max(dot(norm, lightDirection), 0.0);
    // diffuse color
    vec3 diffuseColor = light.diffuseColor * texture(material.diffuseMap,
    TexCoords).rgb;
    diffuseColor = diffuseColor * coeffs.diffuse * costheta * attenuation;

    // ambient term
    // ambient  *= attenuation; // remove attenuation from ambient, as
    // otherwise at large distances the light would be darker inside than
    // outside the spotlight due the ambient term in the else branche
    vec3 ambientTerm = light.ambientColor * texture(material.diffuseMap,
    TexCoords).rgb;
    ambientTerm = ambientTerm * coeffs.ambient; //* attenuation;

    // specular color
    vec3 viewerDirection = normalize(viewerPosition - FragPos);
    vec3 reflectionDirection = reflect(-lightDirection, norm);
    float specularAngle = max(dot(viewerDirection, reflectionDirection), 0.0);
    specularAngle = pow(specularAngle, material.shininess);
    vec3 specular = light.specularColor * texture(material.specularMap,
    TexCoords).rgb;
    specular = specular * specularAngle * coeffs.specular * attenuation;

    vec3 result = specular + ambientTerm + diffuseColor;
    gl_FragColor = vec4(result, 1.0);
  }else{
    // else, use ambient light so scene isn't completely dark outside the
    // spotlight.
    gl_FragColor = vec4(light.ambientColor * texture(
        material.diffuseMap, TexCoords).rgb, 1.0);
      }
}
