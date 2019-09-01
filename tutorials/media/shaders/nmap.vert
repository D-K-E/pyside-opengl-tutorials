#version 330 core
in vec3 aPos;
in vec3 aNormal;
in vec2 aTexCoord;
in vec3 aTangent;
in vec3 aBitangent;

out VS_OUT {
    vec3 FragPos;
    vec2 TexCoord;
    vec3 TangentLightPos;
    vec3 TangentViewPos;
    vec3 TangentFragPos;
} vs_out;

uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

uniform vec3 lightPos;
uniform vec3 viewPos;

void main(void)
{
 vs_out.FragPos = vec3(model * vec4(aPos, 1.0));   
 vs_out.TexCoord = aTexCoord;

 mat3 nMat = transpose(inverse(mat3(model)));
}
