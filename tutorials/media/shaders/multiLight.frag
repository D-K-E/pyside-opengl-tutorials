#version 330 core

out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

struct SunLight { // directional light
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight { // a local light source
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct FlashLight {
    vec3 position;
    vec3 direction;

    float cutOff;
    float outerCutOff;

    float constant;
    float linear;
    float quadratic;
    
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

#define NR_POINT_LIGHTS 3

uniform vec3 viewPosition;
uniform Material material;
uniform SunLight dirLight;
uniform PointLight pLights[NR_POINT_LIGHTS];
uniform PointLight pLight;
uniform FlashLight fLight;

// function prototypes

vec3 computeDirLight(SunLight dLight, 
                     vec3 normal, 
                     vec3 viewDirection);

vec3 computePointLight(PointLight pLight,
                       vec3 normal,
                       vec3 fragPos,
                       vec3 viewDirection);

vec3 computeFlashLight(FlashLight fLight,
                       vec3 normal,
                       vec3 fragPos,
                       vec3 viewDirection);

void main(void)
{
    // properties
    vec3 norm = normalize(Normal);
    vec3 viewDirection = normalize(viewPosition - FragPos);
    // the computation is divided into 3 stages

    // 1: compute directional light or sun light
    vec3 result = computeDirLight(dirLight,
                                  norm,
                                  viewDirection);

    // 2: compute point light that is local light source
    for (int i = 0; i < NR_POINT_LIGHTS; i++)
    {
        PointLight light = pLights[i];
        result = result + computePointLight(
                                light,
                                norm,
                                FragPos,
                                viewDirection);
    }
    result += computePointLight(pLight, norm, 
                                FragPos,
                                viewDirection);
    // stationed somewhere in the world, like a light
    // in a room for example

    // 3: compute flashlight light that is dependent 
    // on the camera position
    result += computeFlashLight(fLight, norm,
                                FragPos,
                                viewDirection);
    vec4 FragColor = vec4(result, 1.0);
}

// compute directional light

vec3 computeDirLight(SunLight dLight, 
                     vec3 normal, 
                     vec3 viewDirection)
{
    vec3 lightDirection = normalize(-dLight.direction);
    // diffuse
    float costheta = max(dot(normal,
                             lightDirection), 0.0);

    // specular
    vec3 reflectDir = reflect(-lightDirection, normal);
    float specAngle = dot(viewDirection, reflectDir);
    float spec = pow(max(specAngle, 0.0),
                     material.shininess);

    // combine all
    vec3 texDiff = texture(material.diffuse,
                           TexCoord).rgb;
    vec3 specDiff = texture(material.specular,
                            TexCoord).rgb;
    vec3 ambient = dLight.ambient * texDiff;
    vec3 diffuse = costheta * dLight.diffuse * texDiff;
    vec3 specular = spec * dLight.specular * specDiff;
    return (ambient + diffuse + specular);
}

// compute point light
vec3 computePointLight(PointLight pLight,
                       vec3 normal,
                       vec3 fragPos,
                       vec3 viewDirection)
{
    vec3 lightDirection = normalize(-pLight.position - fragPos);
    // diffuse
    float costheta = max(dot(normal,
                             lightDirection), 0.0);

    // specular
    vec3 reflectDir = reflect(-lightDirection, normal);
    float specAngle = dot(viewDirection, reflectDir);
    float spec = pow(max(specAngle, 0.0),
                     material.shininess);

    // attenuation
    float dist = length(pLight.position - fragPos);
    float attenuation = pLight.linear * dist;
    attenuation += pLight.quadratic * (dist * dist);
    attenuation += pLight.constant;
    attenuation = min(1.0/attenuation, 1.0);

    // combine all
    vec3 texDiff = texture(material.diffuse,
                           TexCoord).rgb;
    vec3 specDiff = texture(material.specular,
                            TexCoord).rgb;
    vec3 ambient = pLight.ambient * texDiff;
    vec3 diffuse = costheta * pLight.diffuse * texDiff;
    diffuse *= attenuation;
    vec3 specular = spec * pLight.specular * specDiff;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}

// compute flashlight

vec3 computeFlashLight(FlashLight fLight,
                       vec3 normal,
                       vec3 fragPos,
                       vec3 viewDirection)
{
    vec3 lightDirection = normalize(-fLight.direction);
    // diffuse
    float costheta = max(dot(normal,
                             lightDirection), 0.0);

    // specular
    vec3 reflectDir = reflect(-lightDirection, normal);
    float specAngle = dot(viewDirection, reflectDir);
    float spec = pow(max(specAngle, 0.0),
                     material.shininess);

    // intensity of flash light
    float theta = dot(lightDirection,
                      normalize(-fLight.direction));
    float epsilon = fLight.cutOff - fLight.outerCutOff;
    float thetaDiff = theta - fLight.outerCutOff;
    float intensity = thetaDiff / epsilon;
    intensity = clamp(intensity, 0.0, 1.0);

    // attenuation
    float dist = length(fLight.position - fragPos);
    float attenuation = fLight.linear * dist;
    attenuation += fLight.quadratic * (dist * dist);
    attenuation += fLight.constant;
    attenuation = min(1.0/attenuation, 1.0);

    // combine all
    vec3 texDiff = texture(material.diffuse,
                           TexCoord).rgb;
    vec3 specDiff = texture(material.specular,
                            TexCoord).rgb;
    vec3 ambient = fLight.ambient * texDiff;
    vec3 diffuse = costheta * fLight.diffuse * texDiff;
    vec3 specular = spec * fLight.specular * specDiff;

    // obtain final values
    diffuse *= intensity;
    specular *= intensity;
    specular *= attenuation;
    diffuse *= attenuation;
    return (ambient + diffuse + specular);
}
