#version 330 core
in mediump vec3 Normal;
in mediump vec2 TexCoords;
in mediump vec3 FragPos;

out vec4 FragColor;

struct Material {
  sampler2D diffuseMap;  // object picture
  sampler2D specularMap; // normal map
  float shininess;
};

uniform Material material;

struct SpotLight {
  highp vec3 position;
  highp vec3 direction;

  highp vec3 ambientColor;
  highp vec3 diffuseColor;
  highp vec3 specularColor;
};

uniform SpotLight light;

struct Coefficients {
  float lightCutOff;
  float attrConstant;
  float attrLinear;
  float attrQuadratic;
};

uniform Coefficients coeffs;

uniform mediump vec3 viewerPosition;

void main(void) {
    vec3 lightDirection = normalize(light.position - FragPos);
    vec3 texDiffuse = texture(material.diffuseMap, TexCoords).rgb;
    vec3 specText = texture(material.specularMap, TexCoords).rgb;
    vec3 ambient = light.ambientColor * texDiffuse;

    // in spot or not
    float checkValue = dot(lightDirection, normalize(-light.direction));
    if (checkValue > coeffs.lightCutOff)
    {
        // ambient Color

        // diffuse color
        vec3 norm = normalize(Normal);
        float costheta = max(dot(norm, lightDirection), 0.0);
        vec3 diffuse = light.diffuseColor * costheta * texture(material.diffuseMap, TexCoords).rgb;

        // specular color
        vec3 viewerDirection = normalize(viewerPosition - FragPos);
        vec3 reflectionDirection = reflect(-lightDirection, norm);
        float specAngle = max(dot(viewerDirection, reflectionDirection), 0.0);
        specAngle = pow(specAngle, material.shininess);
        vec3 specular = light.specularColor * texture(material.specularMap, TexCoords).rgb * specAngle;

        // attenuation
        float dist = length(light.position - FragPos);
        float attenDist = coeffs.attrLinear * dist;
        attenDist = attenDist + coeffs.attrQuadratic * (dist * dist);
        attenDist = attenDist + coeffs.attrConstant;
        float attenuation = min(1.0 / attenDist, 1.0);

        //
        diffuse = diffuse * attenuation;
        specular = specular * attenuation;

        vec3 result = ambient + diffuse + specular;
        FragColor = vec4(result, 1.0);
    }
    else
    {
        FragColor = vec4(ambient, 1.0);
    }
}

